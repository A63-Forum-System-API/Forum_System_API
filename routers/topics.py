from fastapi import APIRouter, Response, Body
from starlette import status
from schemas.topic import TopicCreate, TopicUpdate
from services import category_service, topic_service

topics_router = APIRouter(prefix='/topics')

#
# @topics_router.get('/')
# def get_all_topics(
#     sort: str | None = None,
#     search: str | None = None,
#     category_id: int | None = None,
#     author_id: int | None = None,
#     status: int | None = None
# ):
#
#     # sorting by created_at
#     # filter by category_id, author_id, is_locked
#     # search by name
#
#     topics = topic_service.get_all_topics(sort, search, category_id, author_id, status)
#
#     if sort and (sort == 'asc' or sort == 'desc'):
#         return topic_service.sort_topics(topics, reverse=sort == 'desc')
#     else:
#         return topics


# @topics_router.get('/{id}')
# def get_topic_by_id(id: int):
#     topic = topic_service.get_by_id(id)
#
#     if topic is None:
#         return Response(content=f"No topic with ID {id} found", status_code=404)
#     else:
#         return topic


@topics_router.post('/', status_code=201)
def create_topic(topic: TopicCreate):
    return topic_service.create(topic)
#
# @topics_router.put('/{id}')
# def lock_topic(id: int):
#     if not topic_service.id_exists(id):
#         return Response(status_code=404)
#
#     topic_service.lock_topic(id)
#
#     return {'message': f'Topic locked successfully.'}