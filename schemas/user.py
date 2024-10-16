from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from pydantic import EmailStr


class User(BaseModel):
    id: Optional[int]
    username: str = Field(
        min_length=5,
        max_length=15,
        regex="^[a-zA-Z0-9_-]+$"
    )
    first_name: str = Field(
        min_length=2,
        max_length=25,
        regex="^[a-zA-Z]+$"
    )
    last_name: str = Field(
        min_length=2,
        max_length=25,
        regex="^[a-zA-Z]+$"
    )
    email: EmailStr
    is_admin: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    picture: Optional[str] = None

    @field_validator('first_name', 'last_name', mode='before')
    def capitalize_names(cls, value):
        return value.capitalize()


class UserCreate(User):
    username: str
    first_name: str
    last_name: str
    email: EmailStr
    password: str = Field(
        min_length=4,
        max_length=36,
        regex=r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$"
    )
    is_admin: bool = False
    picture: Optional[str] = None


class UserLogIn(User):
    username: str
    password: str
