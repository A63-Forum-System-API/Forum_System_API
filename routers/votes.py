from typing import Literal

from fastapi import APIRouter, Depends, Query
from common.auth import get_current_user
from common.custom_responses import BadRequest, NotFound, Locked, ForbiddenAccess, Created, OK
from services import reply_service, vote_service, category_service, user_service, topic_service

votes_router = APIRouter(prefix='/votes', tags=['Votes'])


@votes_router.put('/{reply_id}')
def vote(reply_id: int,
         vote_type: int,
         current_user_id: int = Depends(get_current_user)):

    if vote_type > 1 or vote_type < 0:
        return BadRequest("Votes-type must be 0 for downvote or 1 for upvote")

    reply = reply_service.get_by_id(reply_id)
    if reply is None:
        return NotFound('Reply')

    topic = topic_service.get_by_id(reply.topic_id)
    if topic.is_locked:
        return Locked('topic')

    category = category_service.get_by_id(topic.category_id)
    if not user_service.is_admin(current_user_id) and category.is_private:
        access = category_service.validate_user_access(current_user_id, topic.category_id)
        if not access:
            return ForbiddenAccess()

    vote = vote_service.get_vote(reply_id, current_user_id)
    if vote is None:
        vote_service.create_vote(reply_id, vote_type, current_user_id)
        return Created("User voted successfully")

    if vote == vote_type:
        return BadRequest(f"Current user has already voted for this reply.")

    vote_service.update_vote(reply_id, vote_type, current_user_id)
    vote_str = "upvote" if vote_type == 1 else "downvote"

    return OK(f"Vote is successfully changed to {vote_str}")

@votes_router.delete('/{reply_id}')
def delete_vote(reply_id: int,
                current_user_id: int = Depends(get_current_user)):

    reply = reply_service.get_by_id(reply_id)
    if reply is None:
        return NotFound('Reply')

    topic = topic_service.get_by_id(reply.topic_id)
    if topic.is_locked:
        return Locked('topic')

    category = category_service.get_by_id(topic.category_id)
    if not user_service.is_admin(current_user_id) and category.is_private:
        access = category_service.validate_user_access(current_user_id, topic.category_id)
        if not access:
            return ForbiddenAccess()

    vote = vote_service.get_vote(reply_id, current_user_id)
    if vote is None:
        return BadRequest("User has not voted for this reply")

    vote_service.delete_vote(reply_id, current_user_id)

    return OK("Vote is successfully deleted")