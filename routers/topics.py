from typing import Literal
from fastapi import APIRouter, Depends, Query, Path, Body
from common.auth import get_current_user
from common.custom_responses import ForbiddenAccess, NotFound, OK, Locked, BadRequest, OnlyAdminAccess, OnlyAuthorAccess
from schemas.topic import CreateTopicRequest
from services import topic_service, reply_service, user_service, category_service

topics_router = APIRouter(prefix="/topics", tags=["Topics"])


@topics_router.get("/")
def get_all_topics(
    sort: Literal["asc", "desc"] | None = Query(description="Sort topics by date", default=None),
    search: str | None = Query(description="Search for topics by title", default=None),
    category_id: int | None = Query(description="Filter topics by category ID", default=None),
    author_id: int | None = Query(description="Filter topics by author ID", default=None),
    is_locked: Literal["true", "false"] | None = Query(description="Filter topics by locked status", default=None),
    current_user_id: int = Depends(get_current_user),
    limit: int = Query(description="Limit the number of topics returned", default=10, ge=1, le=100),
    offset: int = Query(description="Offset the number of topics returned", default=0, ge=0)):

    if is_locked is not None:
        is_locked = is_locked == "true"

    if category_id is not None:
        if not category_service.exists(category_id):
            return NotFound(f"Category ID: {category_id}")

        elif not user_service.is_admin(current_user_id):
            if not category_service.validate_user_access(
                    current_user_id, category_id):
                return ForbiddenAccess()

    if author_id is not None and not user_service.id_exists(author_id):
        return NotFound(f"User ID: {author_id}")

    topics = topic_service.get_all_topics(search, category_id, author_id,
                                          is_locked, current_user_id, limit, offset)

    if sort:
        return topic_service.sort_topics(topics, reverse=sort == "desc")

    return topics


@topics_router.get("/{topic_id}")
def get_topic_by_id(topic_id: int = Path(description="ID of the topic to retrieve"),
                    current_user_id: int = Depends(get_current_user)):

    topic = topic_service.get_by_id_with_replies(topic_id)

    if topic is None:
        return NotFound(f"Topic ID: {topic_id}")

    if not user_service.is_admin(current_user_id):
        if not category_service.validate_user_access(
                current_user_id, topic.topic.category_id):
            return ForbiddenAccess()

    return topic


@topics_router.post("/", status_code=201)
def create_topic(topic: CreateTopicRequest = Body(description="Topic to create"),
                 current_user_id: int = Depends(get_current_user)):

    category = category_service.get_by_id(topic.category_id)

    if category is None:
        return NotFound(f"Category ID: {topic.category_id}")

    if category.is_locked:
        return Locked(f"Category ID: {topic.category_id}")

    user_is_admin = user_service.is_admin(current_user_id)

    if not user_is_admin and topic.is_locked == True:
        return OnlyAdminAccess("create locked topics")

    if not user_is_admin and category.is_private:
        access = category_service.validate_user_access(
            current_user_id, topic.category_id, "write")
        if not access:
            return ForbiddenAccess()

    return topic_service.create(topic, current_user_id)


@topics_router.put("/{topic_id}")
def lock_topic(topic_id: int = Path(description="ID of the topic to lock"),
               current_user_id: int = Depends(get_current_user)):
    
    if not user_service.is_admin(current_user_id):
        return OnlyAdminAccess(content="can lock topics")
    
    topic = topic_service.get_by_id(topic_id)
    
    if topic is None:
        return NotFound(f"Topic ID: {topic_id}")

    if topic.is_locked:
        return BadRequest(f"Topic ID: {topic_id} already locked")

    topic_service.lock_topic(topic_id)
    return OK(f"Topic ID: {topic_id} successfully locked")


@topics_router.put("/{topic_id}/replies/{reply_id}")
def chose_topic_best_reply(topic_id: int = Path(description="ID of the topic to choose the best reply for"),
                           reply_id: int = Path(description="ID of the reply to choose as the best reply"),
                           current_user_id: int = Depends(get_current_user)):

    topic = topic_service.get_by_id(topic_id)
    if topic is None:
        return NotFound(f"Topic ID: {topic_id}")

    if topic.is_locked:
        return Locked(f"Topic ID: {topic_id}")

    if not topic_service.validate_topic_author(topic_id, current_user_id):
        return OnlyAuthorAccess("choose best reply for the topic")

    if not reply_service.id_exists(reply_id) or not reply_service.reply_belongs_to_topic(reply_id, topic_id):
        return NotFound(f"Reply ID: {reply_id}")

    prev_best_reply = topic_service.get_topic_best_reply(topic_id)
    if prev_best_reply == reply_id:
        return BadRequest(f"Reply ID: {reply_id} is already the best reply for topic ID: {topic_id}")

    topic_service.update_best_reply(topic_id, reply_id, prev_best_reply)
    return OK(f"Reply ID: {reply_id} is now the best reply for topic ID: {topic_id}")
