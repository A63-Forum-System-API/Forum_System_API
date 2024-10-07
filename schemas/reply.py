from datetime import datetime
from pydantic import BaseModel
from typing_extensions import Optional


class Reply(BaseModel):
    id: Optional[int]
    content: str
    is_best_reply: bool = False
    created_at: datetime = datetime.now()
    topic_id: int
    author_id: int

    @classmethod
    def from_query_result(cls, id, content,
                          is_best_reply, created_at):
        return cls(id=id,
                   content=content,
                   is_best_reply=is_best_reply,
                   created_at=created_at)