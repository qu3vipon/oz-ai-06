from fastapi import FastAPI
from sqlalchemy import text
from connection import SessionFactory


app = FastAPI()

@app.get(
    "/users",
    summary="전체 사용자 조회 API"
)
def get_users_handler():
    with SessionFactory() as session:
        stmt = text("SELECT * FROM user;")
        rows = session.execute(stmt).fetchall()
        users = [row._asdict() for row in rows]
    return {"users": users}
