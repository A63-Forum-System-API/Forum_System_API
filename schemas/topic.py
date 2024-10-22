from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional
from schemas.reply import Reply


class Topic(BaseModel):
    id: Optional[int] = None
    title: str = Field(
        min_length=5,
        max_length=45,
        examples=["Title of topic"]
    )
    content: str = Field(
        min_length=5,
        examples=["This is the content of the topic."]
    )
    is_locked: Optional[bool] = False
    category_id: int
    created_at: Optional[datetime] = datetime.now()
    best_reply_id: Optional[int] = None
    author_id: Optional[int] = None

    @classmethod
    def from_query_result(cls, id, title, content, is_locked, category_id, created_at, best_reply_id, author_id):
        return cls(
            id=id,
            title=title,
            content=content,
            is_locked=is_locked,
            category_id=category_id,
            created_at=created_at,
            best_reply_id=best_reply_id,
            author_id=author_id
        )

class CreateTopicRequest(BaseModel):
    title: str
    content: str
    is_locked: Optional[bool] = False
    category_id: int

class SingleTopic(BaseModel):
    topic: Topic
    all_replies: list[Reply]

class ViewAllTopics(BaseModel):
    id: int
    title: str
    is_locked: bool
    created_at: datetime
    author_id: int
    category_id: int
    replies_count: int

    @classmethod
    def from_query_result(cls, id, title, is_locked, created_at, author_id, category_id, replies_count):
        return cls(
            id=id,
            title=title,
            is_locked=is_locked,
            created_at=created_at,
            author_id=author_id,
            category_id=category_id,
            replies_count=replies_count
        )

class ListOfTopics(BaseModel):
    id: int
    title: str
    is_locked: bool
    created_at: datetime
    author_id: int
    category_id: int

    @classmethod
    def from_query_result(cls, id, title, is_locked, created_at, author_id, category_id):
        return cls(
            id=id,
            title=title,
            is_locked=is_locked,
            created_at=created_at,
            author_id=author_id,
            category_id=category_id,
        )
