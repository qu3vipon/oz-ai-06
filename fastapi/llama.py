from llama_cpp import Llama


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

messages = [
    {"role": "system", "content": SYSTEM_PROMPT}
]

while True:
    # 터미널에 입력한 값
    user_prompt = input("질문을 입력하세요: ")
    messages.append(
        {"role": "user", "content": user_prompt}
    )
    response = llm.create_chat_completion(
        messages=messages,
        max_tokens=512,
        temperature=0.7,  # 확률이 낮은 답변을 생성하도록 -> 창의적 답변
    )

    # 첫번째 답변의 message만 꺼내기
    answer = response["choices"][0]["message"]["content"]
    print(answer)

    # AI 답변을 context로 저장
    messages.append(
        {"role": "assistant", "content": answer}
    )
    print(messages)
