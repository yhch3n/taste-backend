from sqlalchemy import ForeignKey, Column, String, BigInteger, Integer, Float
from db.database import Base
from dataclasses import dataclass


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

@dataclass
class Rating(Base):
    __tablename__ = 'ratings'

    id: int
    user_id: int
    google_place_id: str
    rating: float

    id = Column(BigInteger, primary_key = True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    google_place_id = Column(String(500), nullable=False)
    rating = Column(Float(precision=1), nullable=False)

    def __init__(self, user_id, google_place_id, rating):
        self.user_id = user_id
        self.google_place_id = google_place_id
        self.rating = rating
