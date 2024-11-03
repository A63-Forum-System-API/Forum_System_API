from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from starlette.responses import Response

from common.auth import get_current_user
from common.custom_responses import NotFound
from services import message_service, user_service, conversation_service

conversations_router = APIRouter(prefix="/api/conversations", tags=["Conversations"])


@conversations_router.get("/{receiver_id}")
def view_conversation(receiver_id: int,
                      order: Optional[str] = Query("asc", pattern="^(asc|desc)$"),
                      current_user_id: int = Depends(get_current_user)):
    """
    View a conversation between the current user and the specified receiver.

    Parameters:
        receiver_id (int): The ID of the receiver.
        order (Optional[str]): The order in which to sort the messages (asc or desc).
        current_user_id (int): The ID of the current user (retrieved from the authentication dependency).

    Returns:
        Response: The conversation details or a NotFound response if the user or conversation does not exist.
    """

    if not user_service.id_exists(receiver_id):
        return NotFound(f"User ID: {receiver_id}")

    conversation_id = conversation_service.get_conversation_id(current_user_id, receiver_id)

    if not conversation_id:
        return NotFound(f"Conversation with user ID: {receiver_id}")

    return conversation_service.get_conversation(conversation_id, order)


@conversations_router.get('/')
def view_conversations(current_user_id: int = Depends(get_current_user),
                       order: Optional[str] = Query("asc", pattern="^(asc|desc)$")):
    """
    View all conversations for the current user.

    Parameters:
        current_user_id (int): The ID of the current user (retrieved from the authentication dependency).
        order (Optional[str]): The order in which to sort the conversations (asc or desc).

    Returns:
        Response: A list of conversations or a NotFound response if no conversations are found.
    """

    conversations = conversation_service.get_conversations(current_user_id, order)

    if not conversations:
        return NotFound("Conversations")

    return conversations
