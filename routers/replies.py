from fastapi import APIRouter
from fastapi.openapi.models import Response

from schemas.reply import ReplyBase
from services import topic_service, reply_service

replies_router = APIRouter(prefix='/replies')

@replies_router.post('/', status_code=201)
def create_reply(reply: ReplyBase,
                 current_user: UserFromToken = Depends(get_current_user)):

    topic = topic_service.get_by_id(reply.topic_id)
    if topic is None:
        return Response(content=f"No topic with ID {reply.topic_id} found", status_code=404)

    if topic.is_locked:
        return Response(
            content="This topic is locked.",
            status_code=400)

    return reply_service.create(reply, current_user.id)
