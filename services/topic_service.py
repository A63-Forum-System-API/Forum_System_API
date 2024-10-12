from data.database import insert_query, read_query
from schemas.reply import Reply
from schemas.topic import TopicCreate, TopicsView, TopicView


def get_all_topics(search: str, category_id: int,
                   author_id: int, is_locked: str,
                   limit: int, offset: int):

    is_locked_bool = True if is_locked == 'locked' else False

    query = """SELECT id, title, is_locked, created_at, category_id, author_id FROM topics"""

    params = []
    if search is not None:
        params.append(f"title like '%{search}%'")
    if category_id is not None:
        params.append(f"category_id = {category_id}")
    if author_id is not None:
        params.append(f"author_id = {author_id}")
    if is_locked is not None:
        params.append(f"is_locked = {is_locked_bool}")

    if params:
        query += " WHERE " + " AND ".join(params) + " LIMIT " + str(limit) + " OFFSET " + str(offset)

    topics = read_query(query, params)

    return [
        TopicsView(
            id=id,
            title=title,
            is_locked=is_locked,
            created_at=created_at,
            category_id=category_id,
            author_id=author_id,
        ) for id, title, is_locked, created_at, category_id, author_id in topics]


def get_by_id(topic_id: int):
    query = """SELECT id, title, content, is_locked, 
                created_at, category_id, author_id, best_reply_id 
                FROM topics WHERE id = ?"""

    topic = read_query(query, (topic_id,))
    replies = get_all_replies(topic_id)

    return (TopicView(
        id=id,
        title=title,
        content=content,
        is_locked=is_locked,
        created_at=created_at,
        category_id=category_id,
        author_id=author_id,
        best_reply_id=best_reply_id,
        all_replies=replies
    ) for id, title, content, is_locked, created_at, category_id,
        author_id, best_reply_id  in topic) if topic else None


def get_all_replies(topic_id: int):
    query = """SELECT id, content, created_at, topic_id, author_id FROM replies WHERE topic_id = ?"""

    replies = read_query(query, (topic_id,))

    return [Reply(
        id=id,
        content=content,
        created_at=created_at,
        topic_id=topic_id,
        author_id=author_id
    ) for id, content, created_at, topic_id, author_id in replies]




def create(topic: TopicCreate):
    is_locked_bool = True if topic.is_locked == 'locked' else False

    # # TODO take id of user who is logged in
    author_id = 1

    query = """INSERT INTO topics(title, content, is_locked, category_id, author_id)
                VALUES(?, ?, ?, ?, ?)"""
    params = [topic.title, topic.content, is_locked_bool, topic.category_id, author_id]

    generated_id = insert_query(query, params)
    topic.id = generated_id

    return topic
