# 데이터베이스에서 사용할 테이블 정보를 관리
from sqlalchemy import Integer, String
from sqlalchemy.orm import DeclarativeBase, mapped_column


# 테이블의 공통 부모 클래스
class Base(DeclarativeBase):
    pass

# Item 테이블 & 상품(Item)
class Item(Base):
    __tablename__ = "item"

    id = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    name = mapped_column(String(20))
    price = mapped_column(Integer)
