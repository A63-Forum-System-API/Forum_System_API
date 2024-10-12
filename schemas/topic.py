from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

from schemas.reply import Reply


class TopicBase(BaseModel):
    title: str
    is_locked: bool
    category_id: int
    author_id: int

    class Config:
        fields = {'title': 0, 'is_locked': 1, 'category_id': 2, 'author_id': 3}

class TopicsView(TopicBase):
    id: int
    created_at: datetime
    replies_count: int

    class Config:
        fields = {'id': 0, 'title': 1, 'content': 2, 'is_locked': 3,
                  'created_at': 4, 'category_id': 5, 'author_id': 6,
                  'best_reply_id': 7, 'replies_count': 8, 'all_replies': 9}

class TopicView(TopicBase):
    id: int
    content: str
    created_at: datetime
    best_reply_id: Optional[int]
    replies_count: int
    all_replies: list[Reply]

    class Config:
        fields = {'id': 0, 'title': 1, 'is_locked': 2, 'created_at': 3,
                  'category_id': 4, 'author_id': 5, 'replies_count': 6}

class TopicCreate(TopicBase):
    content: str

    class Config:
        fields = {'title': 0, 'content': 1, 'is_locked': 2,
                  'category_id': 3, 'author_id': 4}


class TopicUpdate(BaseModel):
    is_locked: bool

