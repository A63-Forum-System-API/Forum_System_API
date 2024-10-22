from data.database import insert_query, read_query, update_query
from schemas.reply import Reply
from schemas.topic import ViewAllTopics, Topic, SingleTopic, CreateTopicRequest
from services import user_service

def get_all_topics(search: str | None, category_id: int | None,
                   author_id: int | None, is_locked: bool | None,
                   user_id: int, limit: int, offset: int) -> list[ViewAllTopics]:

    base_query = """SELECT t.id, t.title, t.is_locked, t.created_at, t.author_id , t.category_id, COALESCE(COUNT(r.id), 0) as replies_count
                FROM topics t
                JOIN categories c ON t.category_id = c.id
                LEFT JOIN replies r ON t.id = r.topic_id"""

    # build conditions and params
    where_conditions, params = _build_conditions_and_params(search, category_id,
                                                            author_id, is_locked, user_id)

    # build final query
    final_query, params = _build_final_query(base_query, where_conditions,
                                     params, limit, offset)

    # execute query
    topics = read_query(final_query, (*params,))

    return [ViewAllTopics.from_query_result(*topic) for topic in topics]

def _build_conditions_and_params(search: str | None, category_id: int | None,
                                 author_id: int | None, is_locked: bool | None,
                                 user_id: int) -> tuple:
    where_conditions = []
    params = []

    # check if user is not admin
    if not user_service.is_admin(user_id):
        where_conditions.append("""(c.is_private = 0 OR (c.is_private = 1 AND EXISTS (SELECT 1 FROM category_accesses ca WHERE ca.category_id = t.category_id AND ca.user_id = ?)))""")
        params.append(user_id)

    # check for optional parameters
    if search is not None:
        where_conditions.append("t.title like ?")
        params.append(f'%{search}%')

    if category_id is not None:
        where_conditions.append("t.category_id = ?")
        params.append(category_id)

    if author_id is not None:
        where_conditions.append("t.author_id = ?")
        params.append(author_id)

    if is_locked is not None:
        where_conditions.append("t.is_locked = ?")
        params.append(is_locked)

    return where_conditions, params

def _build_final_query(base_query: str, where_conditions: list,
                       params: list, limit: int, offset: int) -> tuple:
    where_clause = " WHERE " + " AND ".join(where_conditions) if where_conditions else ""
    final_query = f"{base_query}{where_clause} GROUP BY t.id LIMIT ? OFFSET ?"
    params.append(limit)
    params.append(offset)

    return final_query, params

def sort_topics(topics: list[ViewAllTopics],
                reverse=False) -> list[ViewAllTopics]:

    return sorted(topics,  key=lambda t: t.created_at, reverse=reverse)

def get_by_id_with_replies(topic_id: int) -> SingleTopic | None:
    query = """
    SELECT 
        t.id, t.title, t.content, t.is_locked, t.category_id, t.created_at, t.best_reply_id, t.author_id,
        r.id as reply_id, r.content as reply_content, r.topic_id as topic_id, r.created_at as reply_created_at, r.is_best_reply as reply_is_best_reply, r.author_id as reply_author_id,
        SUM(CASE 
                WHEN v.vote_type = True THEN 1 
                WHEN v.vote_type = False THEN -1 
                ELSE 0 
            END) as vote_count
    FROM topics t
    LEFT JOIN replies r ON t.id = r.topic_id
    LEFT JOIN votes v ON r.id = v.reply_id
    WHERE t.id = ?
    GROUP BY t.id, r.id
    """

    data = read_query(query, (topic_id,))
    if not data:
        return None

    # create topic
    topic_data = data[0][:8]
    topic = Topic.from_query_result(*topic_data)

    # create reply list
    replies = [_create_reply_from_row(row) for row in data if row[8]]

    return SingleTopic(topic=topic, all_replies=replies)

def _create_reply_from_row(row) -> Reply:
    reply_data = row[8:]
    reply = Reply.from_query_result(*reply_data)
    reply.vote_count = int(row[14])

    return reply

def get_by_id(topic_id: int) -> Topic | None:
    query = """SELECT id, title, content, is_locked, category_id, created_at, best_reply_id, author_id
                FROM topics
                WHERE id = ?"""

    topic_data = read_query(query, (topic_id,))
    if not topic_data:
        return None

    return Topic.from_query_result(*topic_data[0])

def create(topic: CreateTopicRequest, user_id: int) -> Topic:
    query = """INSERT INTO topics(title, content, is_locked, category_id, author_id)
                VALUES(?, ?, ?, ?, ?)"""

    params = [topic.title, topic.content, topic.is_locked, topic.category_id, user_id]

    generated_id = insert_query(query, (*params,))

    return get_by_id(generated_id)

def id_exists(topic_id: int) -> bool:
    query = """SELECT 1 
                FROM topics 
                WHERE id = ?"""

    result = read_query(query, (topic_id,))

    return len(result) > 0


def lock_topic(topic_id: int) -> None:
    query = """UPDATE topics 
                SET is_locked = True 
                WHERE id = ?"""

    update_query(query, (topic_id,))


def validate_topic_author(topic_id: int, user_id: int) -> bool:
    query = """SELECT 1 
                FROM topics 
                WHERE id = ? AND author_id = ?"""

    result = read_query(query, (topic_id, user_id))

    return len(result) > 0

def update_best_reply(topic_id: int, reply_id: int, prev_best_reply: int | None) -> None:
    if prev_best_reply is not None:
        _mark_reply_as_not_best(prev_best_reply)

    _update_topic_best_reply(topic_id, reply_id)
    _mark_reply_as_best(reply_id)

def get_topic_best_reply(topic_id: int) -> int | None:
    query = """SELECT best_reply_id 
                FROM topics 
                WHERE id = ?"""

    result = read_query(query, (topic_id,))
    if not result:
        return None

    return result[0][0]

def _mark_reply_as_not_best(reply_id: int) -> None:
    query = """UPDATE replies 
                SET is_best_reply = False 
                WHERE id = ?"""

    update_query(query, (reply_id,))

def _update_topic_best_reply(topic_id: int, reply_id: int) -> None:
    query = """UPDATE topics 
                SET best_reply_id = ? 
                WHERE id = ?"""

    update_query(query, (reply_id, topic_id))


def _mark_reply_as_best(reply_id: int) -> None:
    query = """UPDATE replies 
                SET is_best_reply = True 
                WHERE id = ?"""

    update_query(query, (reply_id,))


