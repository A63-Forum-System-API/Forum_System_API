from typing import Literal

from fastapi import APIRouter, Depends, Query, Path
from common.auth import get_current_user
from common.custom_responses import BadRequest, NotFound, Locked, ForbiddenAccess, Created, OK
from services import reply_service, vote_service, category_service, user_service, topic_service

votes_router = APIRouter(prefix="/votes", tags=["Votes"])


@votes_router.put("/{reply_id}")
def vote(reply_id: int = Path(description="ID of the reply to vote for"),
         vote_type: Literal["downvote", "upvote"] = Query(description="Vote ot change vote type"),
         current_user_id: int = Depends(get_current_user)):
    """
    Cast or change a vote for a reply.

    Parameters:
        reply_id (int): The ID of the reply to vote for.
        vote_type (Literal["downvote", "upvote"]): The type of vote to cast or change to.
        current_user_id (int): The ID of the current user, obtained from the authentication dependency.

    Returns:
        JSONResponse: A response indicating the result of the vote operation.
        - 201 Created: If the vote is successfully created.
        - 200 OK: If the vote is successfully changed.
        - 400 Bad Request: If the user has already voted with the same vote type.
        - 404 Not Found: If the reply ID does not exist.
        - 423 Locked: If the topic is locked.
        - 403 Forbidden: If the user does not have access to the category.
    """
    vote_type = 1 if vote_type == "upvote" else 0

    reply = reply_service.get_by_id(reply_id)
    if reply is None:
        return NotFound(f"Reply ID: {reply_id}")

    topic = topic_service.get_by_id(reply.topic_id)
    if topic.is_locked:
        return Locked(f"Topic ID: {reply.topic_id}")

    category = category_service.get_by_id(topic.category_id)
    if not user_service.is_admin(current_user_id) and category.is_private:
        access = category_service.validate_user_access(
            current_user_id, topic.category_id)
        if not access:
            return ForbiddenAccess()

    vote = vote_service.get_vote(reply_id, current_user_id)
    if vote is None:
        vote_service.create_vote(reply_id, vote_type, current_user_id)
        return Created(f"User ID: {current_user_id} voted successfully for reply ID: {reply_id}")

    if vote == vote_type:
        return BadRequest(f"User ID: {current_user_id} has already voted for reply ID: {reply_id}")

    vote_service.update_vote(reply_id, vote_type, current_user_id)
    vote_str = "upvote" if vote_type == 1 else "downvote"

    return OK(f"Vote for reply ID {reply_id} is successfully changed to {vote_str}")


@votes_router.delete("/{reply_id}")
def delete_vote(reply_id: int = Path(description="ID of the reply to delete vote for"),
                current_user_id: int = Depends(get_current_user)):
    """
    Delete a vote for a specific reply and user.

    Parameters:
        reply_id (int): The ID of the reply to delete the vote for.
        current_user_id (int): The ID of the current user, obtained from the authentication dependency.

    Returns:
        JSONResponse: A response indicating the result of the vote deletion.
        - 200 OK: If the vote is successfully deleted.
        - 400 Bad Request: If the user has not voted for the reply.
        - 404 Not Found: If the reply ID does not exist.
        - 423 Locked: If the topic is locked.
        - 403 Forbidden: If the user does not have access to the category.
    """

    reply = reply_service.get_by_id(reply_id)
    if reply is None:
        return NotFound(f"Reply ID: {reply_id}")

    topic = topic_service.get_by_id(reply.topic_id)
    if topic.is_locked:
        return Locked(f"Topic ID: {reply.topic_id}")

    category = category_service.get_by_id(topic.category_id)
    if not user_service.is_admin(current_user_id) and category.is_private:
        access = category_service.validate_user_access(
            current_user_id, topic.category_id)
        if not access:
            return ForbiddenAccess()

    vote = vote_service.get_vote(reply_id, current_user_id)
    if vote is None:
        return BadRequest(f"User ID: {current_user_id} has not voted for reply ID: {reply_id}")

    vote_service.delete_vote(reply_id, current_user_id)

    return OK(f"Vote for reply ID {reply_id} removed successfully")
