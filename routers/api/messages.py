from fastapi import APIRouter, Depends
from starlette.responses import Response

from common.auth import get_current_user
from common.custom_responses import NotFound, BadRequest
from schemas.message import Message
from services import message_service, user_service

messages_router = APIRouter(prefix="/api/messages", tags=["Messages"])


@messages_router.post("/{receiver_id}")
def create_message(receiver_id: int,
                   message: Message,
                   current_user_id: int = Depends(get_current_user)):
    """
    Create a new message for the specified receiver.

    Parameters:
        receiver_id (int): The ID of the receiver.
        message (Message): The message to be sent.
        current_user_id (int): The ID of the current user (retrieved from the authentication dependency).

    Returns:
        Response: A confirmation message indicating the message was sent successfully,
        or an error response if the user does not exist or the message is empty.
    """

    if not user_service.id_exists(receiver_id):
        return NotFound(f"User ID: {receiver_id}")

    if message.text.isspace():
        return BadRequest("Message cannot be empty")

    return message_service.create(message, receiver_id, current_user_id)