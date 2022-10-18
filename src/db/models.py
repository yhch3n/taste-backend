from sqlalchemy import Column, String, BigInteger, Integer
from db.database import Base
from dataclasses import dataclass
from datetime import datetime


@dataclass
class User(Base):
    __tablename__ = 'users'

    id: int
    username: str
    password: str
    country: str
    taste_salty: int
    taste_spicy: int
    taste_sour: int
    taste_sweet: int

    id = Column(BigInteger, primary_key = True, autoincrement=True)
    username = Column(String(100), nullable=False)
    password = Column(String(50), nullable=False)
    country = Column(String(50))
    taste_salty = Column(Integer, default=0)
    taste_spicy = Column(Integer, default=0)
    taste_sour = Column(Integer, default=0)
    taste_sweet = Column(Integer, default=0)

    def __init__(self, username, password):
        self.username = username
        self.password = password
