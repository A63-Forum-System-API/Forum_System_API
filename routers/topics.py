from fastapi import APIRouter, Response, Depends

from common.auth import get_current_user
from schemas.topic import TopicCreate
from services import topic_service, reply_service, user_service, category_service

topics_router = APIRouter(prefix='/topics')


@topics_router.get('/')
def get_all_topics(
    sort: str | None = None,
    search: str | None = None,
    category_id: int | None = None,
    author_id: int | None = None,
    is_locked: bool | None = None,
    limit: int = 10,
    offset: int = 0,
    current_user_id: int = Depends(get_current_user)
):

    if category_id and not category_service.validate_user_access(current_user_id, category_id):
        return Response(content="User does not have access to this category", status_code=403)

    topics = topic_service.get_all_topics(search, category_id, author_id, is_locked, limit, offset)

    accessible_topics = topic_service.accessible_topics(topics, current_user_id)

    if sort and (sort == 'asc' or sort == 'desc'):
        return sorted(accessible_topics, key=lambda t: t.created_at, reverse=sort == 'desc')
    else:
        return accessible_topics


@topics_router.get('/{topic_id}')
def get_topic_by_id(topic_id: int,
                    current_user_id: int = Depends(get_current_user)):

    topic = topic_service.get_by_id(topic_id)

    if topic is None:
        return Response(content=f"No topic with ID {topic_id} found", status_code=404)

    if not category_service.validate_user_access(current_user_id, topic.category_id):
        return Response(content="User does not have access to this category", status_code=403)

    return topic


@topics_router.post('/', status_code=201)
def create_topic(topic: TopicCreate,
                 current_user_id: int = Depends(get_current_user)):

    access = category_service.validate_user_access(current_user_id, topic.category_id)
    if access.write_access:
        return Response(content="User does not have access to write a topic in this category", status_code=403)

    return topic_service.create(topic, current_user_id)


@topics_router.put('/{topic_id}')
def lock_topic(topic_id: int,
               current_user_id: int = Depends(get_current_user)):

    if not topic_service.id_exists(topic_id):
        return Response(content=f"No topic with ID {topic_id} found", status_code=404)

    if not user_service.is_admin(current_user_id):
        return Response(content="Only admins can lock topics", status_code=403)

    topic_service.lock_topic(topic_id)
    return {'message': f'Topic is successfully locked.'}


@topics_router.put('/{topic_id}/replies/{reply_id}')
def chose_topic_best_reply(topic_id: int,
                           reply_id: int,
                           current_user_id: int = Depends(get_current_user)):

    if not topic_service.id_exists(topic_id):
        return Response(content=f"No topic with ID {topic_id} found", status_code=404)

    if not topic_service.validate_topic_author(topic_id, current_user_id):
        return Response(content=f"Current user is not the author of this topic")

    if not reply_service.id_exists(reply_id):
        return Response(content=f"No reply with ID {topic_id} found", status_code=404)

    topic_service.update_best_reply(topic_id, reply_id)

    return {'message': f'Best reply for topic with ID {topic_id} is now reply with ID {reply_id}.'}

