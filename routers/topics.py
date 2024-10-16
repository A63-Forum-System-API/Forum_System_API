from fastapi import APIRouter, Response
from schemas.topic import TopicCreate
from services import topic_service, reply_service

topics_router = APIRouter(prefix='/topics')


@topics_router.get('/')
def get_all_topics(
    sort: str | None = None,
    search: str | None = None,
    category_id: int | None = None,
    author_id: int | None = None,
    is_locked: str | None = None,
    limit: int = 10,
    offset: int = 0,
):

    topics = topic_service.get_all_topics(search, category_id, author_id, is_locked, limit, offset)

    if sort and (sort == 'asc' or sort == 'desc'):
        return sorted(topics, key=lambda t: t.created_at, reverse=sort == 'desc')
    else:
        return topics

@topics_router.get('/{topic_id}')
def get_topic_by_id(topic_id: int):
    topic = topic_service.get_by_id(topic_id)

    if topic is None:
        return Response(content=f"No topic with ID {topic_id} found", status_code=404)
    else:
        return topic


@topics_router.post('/', status_code=201)
def create_topic(topic: TopicCreate,
                 current_user: UserFromToken = Depends(get_current_user)):

    if topic.is_locked not in ['locked', 'not locked']:
        return Response(
            content="Parameter is_locked must be either 'locked' or 'not_locked'",
            status_code=400)

    return topic_service.create(topic, current_user.id)


@topics_router.put('/{topic_id}')
def lock_topic(topic_id: int,
               current_user: UserFromToken = Depends(get_current_user)):

    if not topic_service.id_exists(topic_id):
        return Response(content=f"No topic with ID {topic_id} found", status_code=404)

    if not user_service.is_admin(current_user.id):
        return Response(content="Only admins can lock topics", status_code=403)

    topic_service.lock_topic(topic_id)
    return {'message': f'Topic is successfully locked.'}

@topics_router.put('/{topic_id}/replies/{reply_id}')
def chose_topic_best_reply(topic_id: int,
                           reply_id: int,
                           current_user: UserFromToken = Depends(get_current_user)):

    if not topic_service.id_exists(topic_id):
        return Response(content=f"No topic with ID {topic_id} found", status_code=404)

    if not topic_service.validate_topic_author(topic_id, current_user.id):
        return Response(content=f"Current user is not the author of this topic")

    if not reply_service.id_exists(reply_id):
        return Response(content=f"No reply with ID {topic_id} found", status_code=404)

    topic_service.update_best_reply(topic_id, reply_id)

    return {'message': f'Best reply for topic with ID {topic_id} is now reply with ID {reply_id}.'}



#