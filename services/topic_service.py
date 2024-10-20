from data.database import insert_query, read_query, update_query
from schemas.reply import Reply
from schemas.topic import ViewAllTopics, Topic, SingleTopic
from services import reply_service, user_service


def get_all_topics(search: str, category_id: int,
                   author_id: int, is_locked: bool,
                   limit: int, offset: int, user_id: int):

    user_is_admin = user_service.is_admin(user_id)

    query = """SELECT t.id, t.title, t.is_locked, t.created_at, t.author_id , t.category_id, COALESCE(COUNT(r.id), 0) as replies_count
                FROM topics t
                JOIN categories c ON t.category_id = c.id
                LEFT JOIN replies r ON t.id = r.topic_id"""

    where_conditions = []
    params = []

    if not user_is_admin:
        where_conditions.append("""(c.is_private = 0 OR (c.is_private = 1 AND EXISTS (
                                SELECT 1 FROM category_accesses ca 
                                WHERE ca.category_id = t.category_id AND ca.user_id = ?)))""")
        params.append(user_id)
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

    where_clause = " WHERE " + " AND ".join(where_conditions) if where_conditions else ""
    query = f"{query}{where_clause} GROUP BY t.id LIMIT ? OFFSET ?"
    params.append(limit)
    params.append(offset)

    topics = read_query(query, params)

    return [ViewAllTopics.from_query_result(*topic) for topic in topics]


def get_by_id_with_replies(topic_id: int):
    query = """
    SELECT 
        t.id, t.title, t.content, t.is_locked, t.created_at, t.category_id, t.author_id, t.best_reply_id,
        r.id as reply_id, r.content as reply_content, r.created_at as reply_created_at, r.author_id as reply_author_id,
        SUM(CASE 
                WHEN v.vote_type = True THEN 1 
                WHEN v.vote_type = False THEN -1 
                ELSE 0 
            END) as total_votes
    FROM topics t
    LEFT JOIN replies r ON t.id = r.topic_id
    LEFT JOIN votes v ON r.id = v.reply_id
    WHERE t.id = ?
    GROUP BY t.id, r.id
    """

    data = read_query(query, (topic_id,))

    if not data:
        return None

    topic_data = data[0]
    topic = {
        'id': topic_data[0],
        'title': topic_data[1],
        'content': topic_data[2],
        'is_locked': topic_data[3],
        'created_at': topic_data[4],
        'category_id': topic_data[5],
        'author_id': topic_data[6],
        'best_reply_id': topic_data[7],
    }

    replies = []
    for row in data:
        if row[8]:
            replies.append(Reply(
                id=row[8],
                content=row[9],
                created_at=row[10],
                topic_id=topic_id,
                author_id=row[11],
                total_votes=int(row[12])))

    return SingleTopic(**topic, all_replies=replies)

def get_by_id(topic_id: int):
    query = """SELECT id, title, content, is_locked, category_id, created_at, best_reply_id, author_id
                FROM topics
                WHERE id = ?"""

    topic_data = read_query(query, (topic_id,))

    if not topic_data:
        return None

    return Topic.from_query_result(*topic_data[0])

def create(topic: Topic, user_id: int):
    query = """INSERT INTO topics(title, content, is_locked, category_id, author_id)
                VALUES(?, ?, ?, ?, ?)"""
    params = [topic.title, topic.content, topic.is_locked, topic.category_id, user_id]

    generated_id = insert_query(query, (*params,))

    return get_by_id(generated_id)

def id_exists(topic_id: int):
    query = """SELECT 1 
                FROM topics 
                WHERE id = ?"""
    result = read_query(query, (topic_id,))

    return len(result) > 0


def lock_topic(topic_id: int):
    query = """UPDATE topics 
                SET is_locked = True 
                WHERE id = ?"""
    update_query(query, (topic_id,))


def validate_topic_author(topic_id: int, user_id: int):
    query = """SELECT 1 
                FROM topics 
                WHERE id = ? AND author_id = ?"""
    result = read_query(query, (topic_id, user_id))

    return len(result) > 0


def update_best_reply(topic_id: int, reply_id: int):
    query = """UPDATE topics 
                SET best_reply_id = ? 
                WHERE id = ?"""
    update_query(query, (reply_id, topic_id))

    query = """UPDATE replies 
                SET is_best_reply = True 
                WHERE id = ?"""
    update_query(query, (reply_id,))