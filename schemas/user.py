from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class User(BaseModel):
    id: Optional[int]
    first_name: str
    last_name: str
    email: str
    hash_password: str
    is_admin: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    picture: Optional[str]

    @classmethod
    def from_query_result(cls, id, first_name,
                          last_name, email, is_admin,
                          created_at, picture):
        return cls(id=id,
                   first_name=first_name,
                   last_name=last_name,
                   email=email,
                   is_admin=is_admin,
                   created_at=created_at,
                   picture=picture)

