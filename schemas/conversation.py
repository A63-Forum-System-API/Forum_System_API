from pydantic import BaseModel
from typing import Optional


class Conversation(BaseModel):
    id: Optional[int]
    user1_id: int
    user2_id: int

    @classmethod
    def from_query_result(cls, id, user1_id, user2_id):
        return cls(id=id,
                   user1_id=user1_id,
                   user2_id=user2_id)
