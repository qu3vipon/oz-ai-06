import json
import uuid
from fastapi import FastAPI, Body
from redis import Redis


redis_client = Redis.from_url(
    "redis://redis:6379", 
    decode_responses=True
)

app = FastAPI()

@app.post(
    "/generate",
    summary="Llama 응답 생성 API",
)
def generate_chat_handler(
    user_input: str = Body(..., embed=True)
):
    # 채널 ID 발급
    channel_id = str(uuid.uuid4())

    pubsub = redis_client.pubsub()
    pubsub.subscribe(channel_id)  # 채널 구독

    # Llama 추론 작업 요청 -> Queue 작업 추가
    task = {
        "channel_id": channel_id,  # 결과를 돌려받을 채널 ID
        "user_prompt": user_input,  # 사용자의 질문
    }
    redis_client.lpush("task_queue", json.dumps(task))

    # pub/sub을 통해 결과 반환을 기다림
    for message in pubsub.listen():
        if message["type"] == "message":
            answer = message["data"]
            return answer
