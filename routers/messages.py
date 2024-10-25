from fastapi import APIRouter, Depends
from starlette.responses import Response

from common.auth import get_current_user
from common.custom_responses import NotFound, BadRequest
from schemas.message import Message
from services import message_service, user_service

messages_router = APIRouter(prefix="/messages", tags=["Messages"])


@messages_router.post("/{receiver_id}")
def create_message(receiver_id: int, message: Message, current_user_id: int = Depends(get_current_user)):
    if not user_service.id_exists(receiver_id):
        return NotFound(f"User ID: {receiver_id}")

    if message.text.isspace():
        return BadRequest("Message cannot be empty")

    return message_service.create(message, receiver_id, current_user_id)