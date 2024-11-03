from data.database import read_query, insert_query
from schemas.reply import Reply, CreateReplyRequest


def get_by_id(reply_id: int) -> Reply | None:
    """
    Retrieve a reply by its ID.

    Parameters:
        reply_id (int): The ID of the reply to retrieve.

    Returns:
         Reply | None: The Reply object if found, otherwise None.
     """
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
    """
    Check if a reply exists by its ID.

    Parameters:
        reply_id (int): The ID of the reply to check.

    Returns:
        bool: True if the reply exists, otherwise False.
    """
    query = """SELECT 1 
                FROM replies 
                WHERE id = ?"""

    result = read_query(query, (reply_id,))

    return len(result) > 0


def create(reply: CreateReplyRequest, user_id: int) -> Reply:
    """
    Create a new reply.

    Parameters:
        reply (CreateReplyRequest): The reply data to create.
         user_id (int): The ID of the user creating the reply.

    Returns:
        Reply: The created Reply object.
    """

    query = """INSERT INTO replies(content, topic_id, author_id)
                VALUES(?, ?, ?)"""
    params = [reply.content, reply.topic_id, user_id]

    generated_id = insert_query(query, (*params,))

    return get_by_id(generated_id)


def reply_belongs_to_topic(reply_id: int, topic_id: int) -> bool:
    """
    Check if a reply belongs to a specific topic.

    Parameters:
         reply_id (int): The ID of the reply to check.
         topic_id (int): The ID of the topic to check.

    Returns:
        bool: True if the reply belongs to the topic, otherwise False.
    """
    query = """SELECT 1 
                FROM replies 
                WHERE id = ? 
                AND topic_id = ?"""

    result = read_query(query, (reply_id, topic_id))

    return len(result) > 0


def get_authors_of_replies(replies: list[Reply]) -> dict[int, str]:
    """
    Retrieve the authors of a list of replies.

    Parameters:
        replies (list[Reply]): The list of replies to retrieve the authors for.

    Returns:
        dict[int, str]: A dictionary mapping reply IDs to their usernames.
    """
    reply_ids = [reply.id for reply in replies]

    if not reply_ids:
        return {}

    query = """SELECT r.id, u.username 
                FROM replies r 
                JOIN users u ON r.author_id = u.id
                WHERE r.id IN ({})""".format(", ".join("?" * len(reply_ids)))

    author_data = read_query(query, tuple(reply_ids))

    return {reply_id: username for reply_id, username in author_data}