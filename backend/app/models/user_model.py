from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional


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
    name: str
    email: EmailStr
    password_hash: str
    preferences: UserPreferences = UserPreferences()


class UserResponse(BaseModel):
    name: str
    email: EmailStr
    preferences: UserPreferences