from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class Message(BaseModel):
    id: Optional[int]
    text: str
    sent_at: datetime = Field(default_factory=datetime.now)
    sender_id: int
    receiver_id: int
    conversation_id: int

    @classmethod
    def from_query_result(cls, id, text, sent_at,
                          sender_id, receiver_id,
                          conversation_id):
        return cls(id=id,
                   text=text,
                   sent_at=sent_at,
                   sender_id=sender_id,
                   receiver_id=receiver_id,
                   conversation_id=conversation_id)