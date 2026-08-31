import anyio

from contextlib import asynccontextmanager
from fastapi import FastAPI, Path, Query, Body, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import select
from llama_cpp import Llama

from connection_async import get_async_session
from model import Item


SYSTEM_PROMPT = (
    "You are a concise assistant. "
    "Always reply in the same language as the user's input. "
    "Do not change the language. "
    "Do not mix languages."
)

@asynccontextmanager
async def lifespan(app):
    # 서버가 본격적인 요청을 받기 전에 할 일
    limiter = anyio.to_thread.current_default_thread_limiter()
    limiter.total_tokens = 200  # 스레드풀 개수 200개로

    # llama 모델 로드해서 app.state에 할당
    app.state.llm = Llama(
        model_path="./models/Llama-3.2-1B-Instruct-Q4_K_M.gguf",
        n_ctx=4096,
        n_threads=2,
        verbose=False,
        chat_format="llama-3",
    )
    
    yield
    # 서버를 완전히 종료 하기 전에 할 일


app = FastAPI(lifespan=lifespan)

# request 객체 접근해서 llm 인스턴스 불러오기
def get_llm(request: Request):
    return request.app.state.llm

@app.post(
    "/generate",
    summary="LLM 응답 생성 API",
)
def generate_answer_handler(
    llm = Depends(get_llm),
    user_input: str = Body(..., embed=True),
):
    def token_generator():
        response = llm.create_chat_completion(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input},
            ],
            max_tokens=512,
            temperature=0.7,
            stream=True
        )
        for chunk in response:
            token = chunk["choices"][0]["delta"].get("content")
            if token:
                yield token

    # 계속해서 next()를 호출해서 token_generator 안의 값을 꺼냄
    return StreamingResponse(
        token_generator(),
        media_type="text/event-stream"  # HTTP event-stream
    )

class ItemResponse(BaseModel):
    id: int
    name: str
    price: int

@app.get(
    "/items",
    summary="전체 상품 조회 API",
    response_model=list[ItemResponse]
)
async def get_all_items_handler(
    session = Depends(get_async_session),
):
    stmt = select(Item)
    result = await session.execute(stmt)  # SQL문 실행
    items: list[Item] = result.scalars().all()
    return items

@app.get(
    "/items/search",
    summary="상품 검색 API",
    response_model=list[ItemResponse],
)
async def search_item_handler(
    query: str = Query(..., min_length=2),
    session = Depends(get_async_session)
):  
    # 이름에 query 문자열을 포함하고 있는 상품 조회
    stmt = select(Item).where(Item.name.contains(query))
    result = await session.execute(stmt)
    items = result.scalars().all() # 0~N개
    return items

# Path Parameter
# 1. 다수의 경로를 한 번에 처리하는 API를 만들 때 사용
# 2. 같은 이름의 변수를 핸들러 함수 안으로 전달할 수 있다
# 3. 핸들러 함수로 전달되는 값에 대해서 타입을 지정할 수 있다
@app.get(
    "/items/{item_id}",
    summary="단일 상품 조회 API",
    response_model=ItemResponse
)
async def get_item_handler(
    item_id: int = Path(..., ge=1),  # 1 이상인지 검사
    session = Depends(get_async_session)
):
    stmt = select(Item).where(Item.id == item_id)
    result = await session.execute(stmt)
    item: Item | None = result.scalar()  # 0~1개  

    if item is None:
        raise HTTPException(
            status_code=404,
            detail="아이템을 찾을 수 없습니다."
        )
    return item

# 서버에서 요구하는 Item 등록 데이터 형식
class ItemRegisterRequest(BaseModel):
    name: str
    price: int

@app.post(
    "/items",
    summary="상품 등록 API",
    status_code=201,  # 요청이 성공했을 때, 사용되는 상태코드
    response_model=ItemResponse,
)
async def register_item_handler(
    # 요청 본문의 형식이 ItemRegisterRequest랑 일치해야 된다
    # = 클라이언트는 ItemRegisterRequest에 맞는 데이터를 보내야된다
    body: ItemRegisterRequest,
    session = Depends(get_async_session)
):    
    new_item = Item(name=body.name, price=body.price)
    session.add(new_item)  # 메모리의 session 안에 기록
    await session.commit()  # DB 저장(INSERT INTO ...)
    return new_item

# 수정할 데이터의 형식
class ItemUpdateRequest(BaseModel):
    name: str | None = None
    price: int | None = None

@app.patch(
    "/items/{item_id}",
    summary="상품 수정 API",
    response_model=ItemResponse,
)
async def update_item_handler(
    item_id: int = Path(..., ge=1),
    body: ItemUpdateRequest = Body(...),
    session = Depends(get_async_session)
):
    # 수정할 데이터 조회
    stmt = select(Item).where(Item.id == item_id)
    result = await session.execute(stmt)
    item: Item | None = result.scalar()

    # 없으면 404
    if item is None:
        raise HTTPException(
            status_code=404,
            detail="아이템을 찾을 수 없습니다."
        )

    # 데이터 수정
    if body.name:
        item.name = body.name

    if body.price:
        item.price = body.price

    await session.commit()  # UPDATE SET 쿼리 발생
    return item

@app.delete(
    "/items/{item_id}",
    summary="상품 삭제 API",
    status_code=204,  # 204 NO CONTENT(응답 본문 없음)
    response_model=None,
)
async def delete_item_handler(
    item_id: int = Path(..., ge=1),
    session = Depends(get_async_session)
):
    stmt = select(Item).where(Item.id == item_id)
    result = await session.execute(stmt)
    item: Item | None = result.scalar()

    if item is None:
        raise HTTPException(
            status_code=404,
            detail="아이템을 찾을 수 없습니다."
        )

    await session.delete(item)  # 임시 저장
    await session.commit() 

# await 
# 1) session.close(): 연결 종료
# 2) session.execute(): 쿼리 실행
# 3) session.commit(): 커밋(저장)
# 4) session.delete(): 삭제
