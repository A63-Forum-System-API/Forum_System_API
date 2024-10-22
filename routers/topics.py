from fastapi import APIRouter, Depends
from common.auth import get_current_user
from common.custom_responses import ForbiddenAccess, NotFound, OK, Locked, BadRequest
from schemas.topic import Topic, CreateTopicRequest
from services import topic_service, reply_service, user_service, category_service

topics_router = APIRouter(prefix='/topics')


@topics_router.get('/')
def get_all_topics(
    sort: str | None = None,
    search: str | None = None,
    category_id: int | None = None,
    author_id: int | None = None,
    is_locked: bool | None = None,
    current_user_id: int = Depends(get_current_user),
    limit: int = 10,
    offset: int = 0):

    topics = topic_service.get_all_topics(search, category_id, author_id,
                                          is_locked, current_user_id, limit, offset)

    if sort and (sort == 'asc' or sort == 'desc'):
        return topic_service.sort_topics(topics, key=lambda t: t.created_at, reverse=sort == 'desc')
    else:
        return topics


@topics_router.get('/{topic_id}')
def get_topic_by_id(topic_id: int,
                    current_user_id: int = Depends(get_current_user)):

    topic = topic_service.get_by_id_with_replies(topic_id)

    if topic is None:
        return NotFound('Topic')

    if not user_service.is_admin(current_user_id):
        if not category_service.validate_user_access(current_user_id, topic.category_id):
            return ForbiddenAccess()

    return topic


@topics_router.post('/', status_code=201)
def create_topic(topic: CreateTopicRequest,
                 current_user_id: int = Depends(get_current_user)):

    category = category_service.get_by_id(topic.category_id)

    if category is None:
        return NotFound('Category')

    if category.is_locked:
        return Locked('category')

    user_is_admin = user_service.is_admin(current_user_id)

    if not user_is_admin and topic.is_locked == True:
        return BadRequest('Only admins can create locked topics')

    if not user_is_admin and category.is_private:
        access = category_service.validate_user_access(current_user_id, topic.category_id, access_type='write')
        if not access:
            return ForbiddenAccess()

    return topic_service.create(topic, current_user_id)


@topics_router.put('/{topic_id}')
def lock_topic(topic_id: int,
               current_user_id: int = Depends(get_current_user)):

    topic = topic_service.get_by_id(topic_id)
    if topic is None:
        return NotFound('Topic')

    if topic.is_locked:
        return BadRequest('Topic is already locked')

    if not user_service.is_admin(current_user_id):
        return ForbiddenAccess()

    topic_service.lock_topic(topic_id)
    return OK('Topic is successfully locked')


@topics_router.put('/{topic_id}/replies/{reply_id}')
def chose_topic_best_reply(topic_id: int,
                           reply_id: int,
                           current_user_id: int = Depends(get_current_user)):

    topic = topic_service.get_by_id(topic_id)
    if topic is None:
        return NotFound('Topic')

    if topic.is_locked:
        return Locked('topic')

    if not topic_service.validate_topic_author(topic_id, current_user_id):
        return ForbiddenAccess()

    if not reply_service.id_exists(reply_id) or reply_service.reply_belongs_to_topic(reply_id, topic_id):
        return NotFound('Reply')

    topic_service.update_best_reply(topic_id, reply_id)
    return OK(f'Best reply for topic with ID {topic_id} is now reply with ID {reply_id}.')
