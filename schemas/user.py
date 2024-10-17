from datetime import datetime

from fastapi import HTTPException
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from pydantic import EmailStr
import re
from starlette import status


class User(BaseModel):
    # id: Optional[int]
    username: str = Field(
        min_length=5,
        max_length=15,
        pattern="^[a-zA-Z0-9_-]+$",
        example="example_user"
    )
    first_name: str = Field(
        min_length=2,
        max_length=25,
        pattern="^[a-zA-Z]+$",
        example="Example"
    )
    last_name: str = Field(
        min_length=2,
        max_length=25,
        pattern="^[a-zA-Z]+$",
        example="Example"
    )
    email: EmailStr
    is_admin: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    picture: Optional[str] = None

    @field_validator('first_name', 'last_name', mode='before')
    def capitalize_names(cls, value):
        return value.capitalize()


class UserCreate(User):
    password: str = Field(
        min_length=4,
        max_length=36,
        example="Example123@"
    )

    @field_validator('password')
    def validate_password(cls, value):
        validate = lambda pwd: (
                any(c.isupper() for c in pwd) and
                any(c.islower() for c in pwd) and
                any(c.isdigit() for c in pwd) and
                any(c in '@$!%*?&' for c in pwd)
        )

        if not validate(value):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must contain at least one uppercase letter, one lowercase letter, "
                       "one number, and one special character"
            )
        return value


class UserLogIn(User):
    username: str
    password: str
