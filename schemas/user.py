from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class User(BaseModel):
    id: Optional[int]
    username: str
    first_name: str
    last_name: str
    email: str
    is_admin: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    picture: Optional[str] = None


class UserCreate(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: str
    password: str
    is_admin: bool = False
    picture: Optional[str] = None


class UserLogIn(BaseModel):
    username: str
    password: str
