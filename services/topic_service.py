from data.database import insert_query, read_query, update_query
from schemas.reply import Reply, ReplyBase, ReplyDetailed
from schemas.topic import TopicCreate, TopicsView, TopicView
from services import reply_service


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
        'is_locked': 'locked' if topic_data[3] else 'not locked',
        'created_at': topic_data[4],
        'category_id': topic_data[5],
        'author_id': topic_data[6],
        'best_reply_id': topic_data[7],
    }

    replies = []
    for row in data:
        if row[8]:
            replies.append(ReplyDetailed(
                id=row[8],
                content=row[9],
                created_at=row[10],
                topic_id=topic_id,
                author_id=row[11],
                total_votes=row[12]
            ))

    return TopicView(**topic, all_replies=replies)

def create(topic: TopicCreate, user_id: int):
    is_locked_bool = True if topic.is_locked == 'locked' else False

    query = """INSERT INTO topics(title, content, is_locked, category_id, author_id)
                VALUES(?, ?, ?, ?, ?)"""
    params = [topic.title, topic.content, is_locked_bool, topic.category_id, user_id]

    generated_id = insert_query(query, (*params,))
    topic.id = generated_id

    return topic


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