from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class ReplyBase(BaseModel):
    content: str = Field(
        min_length=5,
        examples=["This is the content of the reply."]
    )
    topic_id: int


class ReplyDetailed(ReplyBase):
    created_at: datetime
    author_id: int
    total_votes: int
