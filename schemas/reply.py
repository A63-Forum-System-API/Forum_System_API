from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class Reply(BaseModel):
    id: Optional[int] = None
    content: str = Field(
        min_length=5,
        examples=["This is the content of the reply."]
    )
    topic_id: int
    created_at: Optional[datetime] = datetime.now()
    is_best_reply: Optional[bool] = False
    author_id: Optional[int] = None
    vote_count: Optional[int] = 0

    @classmethod
    def from_query_result(cls, id, content, topic_id, created_at, is_best_reply, author_id, vote_count):
        return cls(
            id=id,
            content=content,
            topic_id=topic_id,
            created_at=created_at,
            is_best_reply=is_best_reply,
            author_id=author_id,
            vote_count=vote_count
        )

class CreateReplyRequest(BaseModel):
    content: str = Field(
        min_length=5,
        examples=["This is the content of the reply."]
    )
    topic_id: int
