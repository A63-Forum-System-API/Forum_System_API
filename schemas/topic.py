from datetime import datetime
from pydantic import BaseModel
from typing_extensions import Optional


class Topic(BaseModel):
    id: int
    title: str
    content: str
    is_locked: bool = False
    created_at: datetime = datetime.now()
    category_id: int
    author_id: int
    best_reply_id: Optional[int]

