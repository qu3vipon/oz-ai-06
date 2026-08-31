# Type Hints(타입 힌트)
# 변수, 함수, 데이터의 의도된 타입을 코드로 명시하는 문법

# 변수
name: str = "alex"
name = 200

price: int = 200
ratio: float = 0.25
is_active: bool = True

score: int | float = 99.2

# 함수
def add(n1: int, n2: int) -> int:
    return n1 + n2

# 컬렉션 타입(dict, list, tuple, set)
names: list[str] = ["alex", "bob", "chris"]
temperatures: list[int] = [30, 29, 28, 31]
data: list[str | int | bool] = ["alex", 20, "hello", True]

scores: dict[str, int] = {
    # str: int
    "eng": 100, 
    "math": 90
}
