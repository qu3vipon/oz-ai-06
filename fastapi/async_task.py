# 비동기 방식
import asyncio

async def task_a():
    print("A 작업 시작")
    # await time.sleep(2) X -> time.sleep()은 await 불가능
    await asyncio.sleep(2)
    print("A 작업 끝")

async def task_b():
    print("B 작업 시작")
    await asyncio.sleep(2)
    print("B 작업 끝")

async def main():
    # 코루틴 객체 생성
    c1 = task_a()
    c2 = task_b()

    # 코루틴 일괄 실행
    await asyncio.gather(c1, c2)

import time 

start = time.time()

main_coro = main()
asyncio.run(main_coro)

end = time.time()
print(f"실행 시간: {end - start:.2f}")
