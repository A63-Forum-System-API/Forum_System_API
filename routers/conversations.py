from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from starlette.responses import Response

from common.auth import get_current_user
from services import message_service, user_service, conversation_service

conversations_router = APIRouter(prefix='/conversations', tags=['Conversations'])


@conversations_router.get('/{receiver_id}')
def view_conversation(receiver_id: int,
                      order: Optional[str] = Query("asc", pattern="^(asc|desc)$"),
                      current_user_id: int = Depends(get_current_user)):
    if not user_service.id_exists(receiver_id):
        raise HTTPException(status_code=404, detail=f"No user with ID {receiver_id} found")

    conversation_id = conversation_service.get_conversation_id(current_user_id, receiver_id)

    if not conversation_id:
        raise HTTPException(status_code=404, detail=f"No conversation found with user ID {receiver_id}")

    return conversation_service.get_conversation(conversation_id, order)


@conversations_router.get('/')
def view_conversations(current_user_id: int = Depends(get_current_user),
                       order: Optional[str] = Query("asc", pattern="^(asc|desc)$")):

    conversations = conversation_service.get_conversations(current_user_id, order)

    if not conversations:
        raise HTTPException(status_code=404, detail="No conversations found")
    return conversations
