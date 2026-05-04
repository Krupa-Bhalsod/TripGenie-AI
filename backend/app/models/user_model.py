from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from sqlalchemy import Column, Integer, String, JSON
from app.db.sqlite import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    preferences = Column(JSON, default={})


class UserPreferences(BaseModel):
    budget_style: str = "budget"
    preferred_trip_types: List[str] = []
    favorite_destinations: List[str] = []


class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserDB(BaseModel):
    id: Optional[int] = None
    name: str
    email: EmailStr
    password_hash: str
    preferences: UserPreferences = UserPreferences()

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    name: str
    email: EmailStr
    preferences: UserPreferences
