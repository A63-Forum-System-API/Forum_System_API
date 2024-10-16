from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from schemas.reply import ReplyDetailed


class TopicBase(BaseModel):
    id: Optional[int] = None
    title: str
    is_locked: bool | str
    category_id: int


class TopicsView(TopicBase):
    created_at: datetime
    author_id: int


class TopicView(TopicBase):
    content: str
    created_at: datetime
    author_id: int
    best_reply_id: Optional[int]
    all_replies: list[ReplyDetailed]


class TopicCreate(BaseModel):
    id: Optional[int] = None
    title: str
    content: str
    is_locked: bool | str = 'not locked'
    category_id: int
