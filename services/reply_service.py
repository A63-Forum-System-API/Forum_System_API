from data.database import read_query, insert_query
from schemas.reply import ReplyBase, ReplyDetailed


def id_exists(reply_id: int):
    query = """SELECT 1 
                FROM replies 
                WHERE id = ?"""
    result = read_query(query, (reply_id,))

    return len(result) > 0


def create(reply: ReplyBase, user_id: int):

    query = """INSERT INTO replies(content, topic_id, author_id)
                VALUES(?, ?, ?)"""
    params = [reply.content, reply.topic_id, user_id]

    generated_id = insert_query(query, (*params,))
    reply.id = generated_id

    return reply


def parse_replies_data(data):
    replies = []

    for row in data:
        if row[8]:
            id, content, topic_id, created_at, author_id = row[8:13]

            query = """SELECT 
                            SUM(CASE 
                                WHEN vote_type = True THEN 1
                                WHEN vote_type = False THEN -1
                                ELSE 0
                            END) as total_rating
                        FROM votes
                        WHERE reply_id = ?"""

            votes_data = read_query(query, (id,))
            total_votes = votes_data[0][0]

            reply = ReplyDetailed(
        id=id,
        content=content,
        created_at=created_at,
        topic_id=topic_id,
        author_id=author_id,
        total_votes=total_votes)
            replies.append(reply)

    return replies