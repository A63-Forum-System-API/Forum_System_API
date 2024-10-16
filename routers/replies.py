from fastapi import APIRouter, Depends, HTTPException
from fastapi.openapi.models import Response

from common.auth import get_current_user
from schemas.reply import ReplyBase
from services import topic_service, reply_service

replies_router = APIRouter(prefix='/replies')


@replies_router.post('/', status_code=201)
def create_reply(reply: ReplyBase,
                 current_user_id: int = Depends(get_current_user)):

    topic = topic_service.get_by_id(reply.topic_id)
    if topic is None:
        return Response(content=f"No topic with ID {reply.topic_id} found", status_code=404)

    if topic.is_locked == 'locked':
        raise HTTPException(
            status_code=400,
            detail="This topic is locked.")

    return reply_service.create(reply, current_user_id)
