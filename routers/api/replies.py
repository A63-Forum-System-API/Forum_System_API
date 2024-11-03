from fastapi import APIRouter, Depends, Body
from common.auth import get_current_user
from common.custom_responses import ForbiddenAccess, NotFound, Locked
from data.database import read_query
from schemas.reply import Reply, CreateReplyRequest
from services import topic_service, reply_service, category_service, user_service

replies_router = APIRouter(prefix="/api/replies", tags=["Replies"])


@replies_router.post("/", status_code=201)
def create_reply(reply: CreateReplyRequest = Body(description="Reply to create"),
                 current_user_id: int = Depends(get_current_user)):
    """
    Create a new reply to a topic.

    Parameters:
        reply (CreateReplyRequest): The reply data to create.
        current_user_id (int): The ID of the current user, obtained from the authentication dependency.

    Returns:
        JSONResponse: A response indicating the result of the reply creation.
        - 201 Created: If the reply is successfully created.
        - 404 Not Found: If the topic ID does not exist.
        - 423 Locked: If the topic is locked.
        - 403 Forbidden: If the user does not have access to the category.
    """
    topic = topic_service.get_by_id(reply.topic_id)

    if topic is None:
        return NotFound(f"Topic ID: {reply.topic_id}")

    if topic.is_locked:
        return Locked(f"Topic ID: {reply.topic_id}")
    
    category = category_service.get_by_id(topic.category_id)

    if not user_service.is_admin(current_user_id) and category.is_private:
        access = category_service.validate_user_access(current_user_id, topic.category_id, access_type="write")
        if not access:
            return ForbiddenAccess()

    return reply_service.create(reply, current_user_id)
