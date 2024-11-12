from sqlalchemy import Column, Integer, String
from db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(String, unique=True)
    name = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)




