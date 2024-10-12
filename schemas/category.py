from datetime import datetime
from pydantic import BaseModel
from schemas.topic import TopicsView
from typing import Optional


class Category(BaseModel):
    id: int
    title: str
    description: str
    is_private: bool = False
    is_locked: bool = False
    created_at: datetime | None = datetime.now()
    admin_id: int
    # topics: Optional[list] = None


    @classmethod
    def from_query_result(cls, id, title, description, is_private, is_locked, created_at, admin_id):
        return cls(id=id,
                   title=title,
                   description=description,
                   is_private=is_private,
                   is_locked=is_locked,
                   created_at=created_at,
                   admin_id=admin_id)
    

class SingleCategory(BaseModel):
    category: Category
    topics: list[TopicsView]


class ViewAllCategories(BaseModel):
    id: int
    title: str
    description: str
    created_at: datetime = datetime.now()