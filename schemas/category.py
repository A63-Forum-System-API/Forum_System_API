from datetime import datetime
from pydantic import BaseModel, Field
from schemas.topic import ViewAllTopics, ListOfTopics
from typing import Optional


class Category(BaseModel):
    id: Optional[int] = None
    title: str = Field(
        min_length=5,
        max_length=45,
        examples=["Title for category."]
    )
    description: str = Field(
        min_length=5,
        examples=["Short description of the category."]
    )
    is_private: bool = False
    is_locked: Optional[bool] = False
    created_at: Optional[datetime] = datetime.now()
    admin_id: Optional[int] = None
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
    topics: list[ListOfTopics]


class ViewAllCategories(BaseModel):
    id: int
    title: str
    description: str
    is_private: bool
    is_locked: bool
    created_at: datetime = datetime.now() 

    @classmethod
    def from_query_result(cls, id, title, description, is_private, is_locked, created_at):
        return cls(id=id,
                   title=title,
                   description=description,
                   is_private=is_private,
                   is_locked=is_locked,
                   created_at=created_at)


class CreateCategoryRequest(BaseModel):
    title: str = Field(
        min_length=5,
        max_length=45,
        examples=["Title for category."]
    )
    description: str = Field(
        min_length=5,
        examples=["Short description of the category."]
    )
    is_private: bool = False