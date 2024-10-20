from typing import Optional

from fastapi import APIRouter, Depends, Query
from starlette.responses import Response

from common.auth import get_current_user
from schemas.conversation import Conversation
from services import message_service, user_service, conversation_service

conversations_router = APIRouter(prefix='/conversations')


@conversations_router.get('/{receiver_id}')
def view_conversation(receiver_id: int,
                      order: Optional[str] = Query("asc", pattern="^(asc|desc)$"),
                      current_user_id: int = Depends(get_current_user)):
    if not user_service.id_exists(receiver_id):
        return Response(content=f"No user with ID {receiver_id} found!", status_code=404)

    conversation_id = conversation_service.get_conversation_id(current_user_id, receiver_id)

    if not conversation_id:
        return Response(content=f"No conversation between users with IDs {current_user_id} and {receiver_id} found!",
                        status_code=404)

    return conversation_service.get_conversation(conversation_id, order)
