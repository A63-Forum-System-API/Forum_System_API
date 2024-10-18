from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional
from schemas.reply import ReplyDetailed


class TopicBase(BaseModel):
    id: Optional[int] = None
    title: str = Field(
        min_length=5,
        max_length=45,
        examples=["Title of topic"]
    )
    category_id: int
    is_locked: bool = False


class TopicsView(TopicBase):
    created_at: datetime
    author_id: int



class TopicView(TopicBase):
    content: str = Field(
        min_length=5,
        max_length=45,
        examples=["Title of topic"]
    )
    created_at: datetime
    author_id: int
    best_reply_id: Optional[int]
    all_replies: list[ReplyDetailed]


class TopicCreate(TopicBase):
    content: str = Field(
        min_length=5,
        examples=["This is the content of the topic."]
    )