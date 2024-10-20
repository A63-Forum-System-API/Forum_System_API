from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class Message(BaseModel):
    text: str = Field(
        max_length=500,
        examples=["This is the content of the message."]
    )
    # receiver_id: int
    # conversation_id: int

    # @classmethod
    # def from_query_result(cls, text, sent_at,
    #                       receiver_id, conversation_id):
    #     return cls(text=text,
    #                sent_at=sent_at,
    #                receiver_id=receiver_id,
    #                conversation_id=conversation_id)
