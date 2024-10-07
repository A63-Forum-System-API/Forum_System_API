from datetime import datetime
from pydantic import BaseModel
from typing_extensions import Optional


class Topic(BaseModel):
    id: Optional[int]
    title: str
    content: str
    is_locked: bool = False
    created_at: datetime = datetime.now()
    category_id: int
    author_id: int
    best_reply_id: Optional[int]

    @classmethod
    def from_query_result(cls, id, content,
                          is_locked, created_at, category_id,
                          author_id, best_reply_id):
        return cls(id=id,
                   content=content,
                   is_locked=is_locked,
                   created_at=created_at,
                   category_id=category_id,
                   author_id=author_id,
                   best_reply_id=best_reply_id)

