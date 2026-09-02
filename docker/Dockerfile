# Base image 선택
FROM python:3.13-slim
# image 내의 작업경로 지정
WORKDIR /app
# 전체 파일을 도커 내부로 복사
COPY . .
# docker build 과정에서 실행되는 명령어
RUN pip install "fastapi[standard]"
RUN pip install sqlalchemy pymysql cryptography

# docker run 했을 때, FastAPI 서버 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]