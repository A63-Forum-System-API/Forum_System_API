from data.database import read_query, insert_query
from schemas.reply import Reply


def get_by_id(reply_id: int):
    query = """SELECT id, content, topic_id, created_at, is_best_reply, author_id
                FROM replies
                WHERE id = ?"""

    reply_data = read_query(query, (reply_id,))

    if not reply_data:
        return None

    return Reply.from_query_result(*reply_data[0])

def id_exists(reply_id: int):
    query = """SELECT 1 
                FROM replies 
                WHERE id = ?"""
    result = read_query(query, (reply_id,))

    return len(result) > 0


def create(reply: Reply, user_id: int):

    query = """INSERT INTO replies(content, topic_id, author_id)
                VALUES(?, ?, ?)"""
    params = [reply.content, reply.topic_id, user_id]

    generated_id = insert_query(query, (*params,))


    return get_by_id(generated_id)

#
# def parse_replies_data(data):
#     replies = []
#
#     for row in data:
#         if row[8]:
#             id, content, topic_id, created_at, author_id = row[8:13]
#
#             query = """SELECT
#                             SUM(CASE
#                                 WHEN vote_type = True THEN 1
#                                 WHEN vote_type = False THEN -1
#                                 ELSE 0
#                             END) as total_rating
#                         FROM votes
#                         WHERE reply_id = ?"""
#
#             votes_data = read_query(query, (id,))
#             total_votes = votes_data[0][0]
#
#             reply = ReplyDetailed(
#                     id=id,
#                     content=content,
#                     created_at=created_at,
#                     topic_id=topic_id,
#                     author_id=author_id,
#                     total_votes=total_votes,
#                     is_best_reply=False)
#
#             replies.append(reply)
#
#     return replies


def get_reply_by_id(reply_id: int):
    query = """SELECT content, topic_id
                FROM replies
                WHERE id = ?"""

    reply_data = read_query(query, (reply_id,))

    reply = reply_data[0]
    return Reply(content=reply[0], topic_id=reply[1])