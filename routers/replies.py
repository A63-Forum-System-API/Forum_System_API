from fastapi import APIRouter, Depends
from common.auth import get_current_user
from common.custom_responses import ForbiddenAccess, NotFound, Locked
from data.database import read_query
from schemas.reply import Reply, CreateReplyRequest
from services import topic_service, reply_service, category_service, user_service

replies_router = APIRouter(prefix='/replies')


@replies_router.post('/', status_code=201)
def create_reply(reply: CreateReplyRequest,
                 current_user_id: int = Depends(get_current_user)):

    topic = topic_service.get_by_id(reply.topic_id)
    category = category_service.get_by_id(topic.category_id)

    if topic is None:
        return NotFound('Topic')

    if topic.is_locked:
        return Locked('topic')

    if not user_service.is_admin(current_user_id) and category.is_private:
        access = category_service.validate_user_access(current_user_id, topic.category_id, access_type='write')
        if not access:
            return ForbiddenAccess()

    return reply_service.create(reply, current_user_id)
