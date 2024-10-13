from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

from schemas.reply import Reply


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
    all_replies: list[Reply]


class TopicCreate(TopicBase):
    content: str
    is_locked: str = "not locked"


class TopicUpdate(BaseModel):
    is_locked: bool

