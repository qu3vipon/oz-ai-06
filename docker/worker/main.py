import json
from llama_cpp import Llama
from redis import Redis


redis_client = Redis.from_url(
    "redis://redis:6379",
    decode_responses=True,
    socket_timeout=None,  # Timeout 발생 방지
)

llm = Llama(
    model_path="./models/Llama-3.2-1B-Instruct-Q4_K_M.gguf",
    n_ctx=4096,
    n_threads=2,
    verbose=False,
    chat_format="llama-3",
)

SYSTEM_PROMPT = (
    "You are a concise assistant. "
    "Always reply in the same language as the user's input. "
    "Do not change the language. "
    "Do not mix languages."
)

def run():
    # worker가 계속 동작
    while True:
        # 1) Queue에서 작업을 꺼내기(작업이 있을 때까지 기다림)
        _, task = redis_client.brpop("task_queue")
        task_dict = json.loads(task)  # JSON -> Python

        channel_id = task_dict["channel_id"]
        user_prompt = task_dict["user_prompt"]

        # 2) 추론
        response = llm.create_chat_completion(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=256,
            temperature=0.7
        )
        answer = response["choices"][0]["message"]["content"]

        # 3) 결과를 알려줌(Publish)
        redis_client.publish(channel_id, answer)

# 이 파일을 직접 실행한 경우에만, run() 실행
if __name__ == "__main__":
    run()
