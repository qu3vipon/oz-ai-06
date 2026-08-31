# Pydantic
# 데이터 검증/파싱을 담당하는 라이브러리

from pydantic import BaseModel


# pydantic
class Item(BaseModel):
    name: str
    price: int

# python 기본 클래스 문법
class Item2:
    def __init__(self, name, price):
        self.name = name
        self.price = price
