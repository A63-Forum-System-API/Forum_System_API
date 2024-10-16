from data.database import insert_query, read_query, update_query
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
            is_locked='locked' if is_locked else 'not locked',
            created_at=created_at,
            category_id=category_id,
            author_id=author_id,
        ) for id, title, is_locked, created_at, category_id, author_id in topics]


def get_by_id(topic_id: int):
    query = """SELECT t.*, r.*
                FROM topics t
                LEFT JOIN replies r ON t.id = r.topic_id
                WHERE t.id = ?"""

    data = read_query(query, (topic_id,))

    topic = parse_topic_data(data[0])
    replies = parse_replies_data(data)

    if not topic:
        return None

    return TopicView(**topic, all_replies=replies)

def parse_topic_data(data):
    id, title, content, is_locked, created_at, category_id, author_id, best_reply_id = data[:8]
    return {
        'id': id,
        'title': title,
        'content': content,
        'is_locked': 'locked' if is_locked else 'not locked',
        'created_at': created_at,
        'category_id': category_id,
        'author_id': author_id,
        'best_reply_id': best_reply_id,
    }

def parse_replies_data(data):
    replies = []
    for row in data:
        if row[8]:
            id, content, topic_id, created_at, author_id = row[8:13]
            reply = Reply(
        id=id,
        content=content,
        created_at=created_at,
        topic_id=topic_id,
        author_id=author_id)
            replies.append(reply)

    return replies


def create(topic: TopicCreate, user_id: int):
    is_locked_bool = True if topic.is_locked == 'locked' else False

    query = """INSERT INTO topics(title, content, is_locked, category_id, author_id)
                VALUES(?, ?, ?, ?, ?)"""
    params = [topic.title, topic.content, is_locked_bool, topic.category_id, user_id]

    generated_id = insert_query(query, params)
    topic.id = generated_id

    return topic


def id_exists(topic_id: int):
    query = """SELECT 1 FROM topics WHERE id = ?"""
    result = read_query(query, (topic_id,))

    return len(result) > 0


def lock_topic(topic_id: int):

    query = """UPDATE topics SET is_locked = True WHERE id = ?"""
    update_query(query, (topic_id,))

    return True