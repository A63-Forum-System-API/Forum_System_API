from pydantic import BaseModel


class Vote(BaseModel):
    reply_id: int
    vote_type: int