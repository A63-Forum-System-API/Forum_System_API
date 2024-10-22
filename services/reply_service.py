from data.database import read_query, insert_query
from schemas.reply import Reply, CreateReplyRequest


def get_by_id(reply_id: int) -> Reply | None:
    query = """SELECT r.id, r.content, r.topic_id, r.created_at, r.is_best_reply, r.author_id,
            SUM(CASE 
                WHEN v.vote_type = True THEN 1 
                WHEN v.vote_type = False THEN -1 
                ELSE 0 
            END) as vote_count
    FROM replies r
    LEFT JOIN votes v ON r.id = v.reply_id
    WHERE r.id = ?
    GROUP BY r.id"""

    reply_data = read_query(query, (reply_id,))

    if not reply_data:
        return None

    return Reply.from_query_result(*reply_data[0])


def id_exists(reply_id: int) -> bool:
    query = """SELECT 1 
                FROM replies 
                WHERE id = ?"""

    result = read_query(query, (reply_id,))

    return len(result) > 0


def create(reply: CreateReplyRequest, user_id: int) -> Reply:

    query = """INSERT INTO replies(content, topic_id, author_id)
                VALUES(?, ?, ?)"""
    params = [reply.content, reply.topic_id, user_id]

    generated_id = insert_query(query, (*params,))

    return get_by_id(generated_id)


def reply_belongs_to_topic(reply_id: int, topic_id: int) -> bool:
    query = """SELECT 1 
                FROM replies 
                WHERE id = ? 
                AND topic_id = ?"""

    result = read_query(query, (reply_id, topic_id))

    return len(result) > 0

