from fastapi import APIRouter, Depends
from starlette.responses import Response

from common.auth import get_current_user
from schemas.message import Message
from services import message_service, user_service

messages_router = APIRouter(prefix='/messages')


@messages_router.post('/{receiver_id}')
def create_message(receiver_id: int, message: Message, current_user_id: int = Depends(get_current_user)):
    if not user_service.id_exists(receiver_id):
        return Response(content=f"No user with ID {receiver_id} found", status_code=404)

    if message.text.isspace():
        return Response(content="Message cannot be empty", status_code=400)

    return message_service.create(message, receiver_id, current_user_id)