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
    """
    Retrieve all topics based on the provided filters.

    Parameters:
        sort (Literal["asc", "desc"] | None): Sort topics by date.
        search (str | None): Search for topics by title.
        category_id (int | None): Filter topics by category ID.
        author_id (int | None): Filter topics by author ID.
        is_locked (Literal["true", "false"] | None): Filter topics by locked status.
        current_user_id (int): The ID of the current user, obtained from the authentication dependency.
        limit (int): Limit the number of topics returned.
        offset (int): Offset the number of topics returned.

    Returns:
        JSONResponse: A response containing the list of topics matching the filters.
        - 200 OK: If the topics are successfully retrieved.
        - 404 Not Found: If the category or author ID does not exist.
        - 403 Forbidden: If the user does not have access to the category.
    """

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
    """
    Retrieve a topic by its ID along with its replies.

    Parameters:
        topic_id (int): The ID of the topic to retrieve.
        current_user_id (int): The ID of the current user, obtained from the authentication dependency.

    Returns:
        JSONResponse: A response containing the topic and its replies.
        - 200 OK: If the topic is successfully retrieved.
        - 404 Not Found: If the topic ID does not exist.
        - 403 Forbidden: If the user does not have access to the category.
    """

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
    """
    Create a new topic.

    Parameters:
        topic (CreateTopicRequest): The topic data to create.
        current_user_id (int): The ID of the current user (retrieved from the authentication dependency).

    Returns:
        JSONResponse: A response indicating the result of the topic creation.
        - 201 Created: If the topic is successfully created.
        - 404 Not Found: If the category ID does not exist.
        - 423 Locked: If the category is locked.
        - 403 Forbidden: If the user does not have access to the category.
        - 403 OnlyAdminAccess: If a non-admin user tries to create a locked topic.
    """
    category = category_service.get_by_id(topic.category_id)

    if category is None:
        return NotFound(f"Category ID: {topic.category_id}")

    user_is_admin = user_service.is_admin(current_user_id)

    if not user_is_admin and category.is_private:
        access = category_service.validate_user_access(
            current_user_id, topic.category_id, "write")
        if not access:
            return ForbiddenAccess()

    if category.is_locked:
        return Locked(f"Category ID: {topic.category_id}")

    if not user_is_admin and topic.is_locked == True:
        return OnlyAdminAccess("create locked topics")

    return topic_service.create(topic, current_user_id)


@topics_router.put("/{topic_id}/locked-status/{locked_status}")
def change_topic_lock_status(topic_id: int = Path(description="ID of the topic to lock/unlock"),
                             locked_status: Literal["lock", "unlock"] = Path(description="Lock status for the topic"),
                             current_user_id: int = Depends(get_current_user)):
    """
    Change the lock status of a topic.

    Parameters:
        topic_id (int): The ID of the topic to lock/unlock.
        locked_status (Literal["lock", "unlock"]): The lock status for the topic.
        current_user_id (int): The ID of the current user, obtained from the authentication dependency.

    Returns:
        JSONResponse: A response indicating the result of the lock status change.
        - 200 OK: If the lock status is successfully changed.
        - 404 Not Found: If the topic ID does not exist.
        - 403 OnlyAdminAccess: If the user is not an admin.
    """
    if not user_service.is_admin(current_user_id):
        return OnlyAdminAccess(content="change locked status for topics")

    locked_status_code = 1 if locked_status == "lock" else 0
    
    topic = topic_service.get_by_id(topic_id)
    if topic is None:
        return NotFound(f"Topic ID: {topic_id}")

    if topic.is_locked == locked_status_code:
        return OK(f"Topic ID: {topic_id} is already {locked_status}ed")

    topic_service.change_topic_lock_status(locked_status_code, topic_id)
    return OK(f"Topic ID: {topic_id} successfully locked")


@topics_router.put("/{topic_id}/replies/{reply_id}")
def chose_topic_best_reply(topic_id: int = Path(description="ID of the topic to choose the best reply for"),
                           reply_id: int = Path(description="ID of the reply to choose as the best reply"),
                           current_user_id: int = Depends(get_current_user)):
    """
    Choose the best reply for a topic.

    Parameters:
        topic_id (int): The ID of the topic to choose the best reply for.
        reply_id (int): The ID of the reply to choose as the best reply.
        current_user_id (int): The ID of the current user, obtained from the authentication dependency.

    Returns:
        JSONResponse: A response indicating the result of the best reply selection.
        - 200 OK: If the best reply is successfully chosen.
        - 400 Bad Request: If the reply is already the best reply.
        - 404 Not Found: If the topic or reply ID does not exist.
        - 423 Locked: If the topic is locked.
        - 403 OnlyAuthorAccess: If the user is not the author of the topic.
    """
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
