# 동기식 작업
import time

def task_a():
    print("A 작업 시작")
    time.sleep(2)  # 2초 대기발생(I/O 작업)
    print("A 작업 끝")

def task_b():
    print("B 작업 시작")
    time.sleep(2)  # 2초 대기발생(I/O 작업)
    print("B 작업 끝")

start = time.time()
task_a()
task_b()
end = time.time()
print(f"실행 시간: {end - start:.2f}")
