from datetime import datetime
from fastapi import HTTPException
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from pydantic import EmailStr
import re
from starlette import status


class User(BaseModel):
    username: str = Field(
        min_length=5,
        max_length=15,
        pattern="^[a-zA-Z0-9_-]+$",
        examples=["example_user"]
    )
    first_name: str = Field(
        min_length=2,
        max_length=25,
        pattern="^[a-zA-Z]+(?:-[a-zA-Z]+)?$",
        examples=["Example"]
    )
    last_name: str = Field(
        min_length=2,
        max_length=25,
        pattern="^[a-zA-Z]+(?:-[a-zA-Z]+)?$",
        examples=["Example"]
    )
    email: EmailStr
    picture: Optional[str] = Field(
        None,
        examples=["https://example.com/user-picture.png"]
    )

    @field_validator('first_name', 'last_name', mode='before')
    def capitalize_names(cls, value):
        return value.capitalize()


class UserCreate(User):
    password: str = Field(
        min_length=4,
        max_length=36,
        examples=["Example123@"]
    )

    @field_validator('password')
    def validate_password(cls, value):
        validate = lambda pwd: (
                any(c.isupper() for c in pwd) and
                any(c.islower() for c in pwd) and
                any(c.isdigit() for c in pwd) and
                any(c in '@$!%*?&' for c in pwd) and
                not any(c.isspace() for c in pwd)
        )

        if not validate(value):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must contain at least one uppercase letter, one lowercase letter, "
                       "one number, and one special character and must not contain any spaces"
            )
        return value


class UserLogIn(BaseModel):
    username: str
    password: str


class UserUpdate(BaseModel):
    is_admin: bool
