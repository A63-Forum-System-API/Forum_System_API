from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class ReplyBase(BaseModel):
    id: Optional[int] = None
    content: str
    topic_id: int


class ReplyDetailed(ReplyBase):
    is_best_reply: bool
    created_at: datetime
    author_id: int
    total_votes: int
