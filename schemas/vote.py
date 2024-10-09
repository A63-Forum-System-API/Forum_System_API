from pydantic import BaseModel
from typing import Optional


class Vote(BaseModel):
    id: Optional[int]
    up_vote: bool = False
    down_vote: bool = False
    reply_id: int
    user_id: int

    @classmethod
    def from_query_result(cls, id, up_vote, down_vote, reply_id, user_id):
        return cls(id=id,
                   up_vote=up_vote,
                   down_vote=down_vote,
                   reply_id=reply_id,
                   user_id=user_id)

