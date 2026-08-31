# SQLAlchemy를 이용해서 데이터베이스 연결할 때 필요한 설정
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


# 데이터베이스 접속 정보
DATABASE_URL = "sqlite+aiosqlite:///fastapi.db"

# Engine: DB 연결을 맺는 객체, 모든 명령이 엔진을 통해 실행
# echo=True: SQLAlchemy가 데이터베이스에 발생시키는 명령 출력
async_engine = create_async_engine(DATABASE_URL, echo=True)

# Session: 데이터베이스에 요청/응답을 주고받는 하나의 짧은 기간
AsyncSessionFactory = async_sessionmaker(
    bind=async_engine, 
    autoflush=False, 
    autocommit=False, 
    expire_on_commit=False,
)

# 세션 생성/종료를 담당하는 함수
async def get_async_session():
    session = AsyncSessionFactory()
    try:
        yield session
    finally:
        await session.close()
