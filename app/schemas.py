from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str


class AccessToken(BaseModel):
    access_token: str
    token_type: str


class RefreshToken(BaseModel):
    refresh_token: str


class TokenData(BaseModel):
    user_id: Optional[str] = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    deadline: Optional[date] = None
    completed: bool
    last_update: datetime
    owner_id: int
    owner: UserResponse

    class Config:
        orm_mode = True


class TaskCreate(BaseModel):
    title: str
    description: str
    deadline: Optional[date] = None


class TaskComplete(BaseModel):
    completed: bool
