from data.database import insert_query, read_query, update_query
from schemas.reply import Reply
from schemas.topic import ViewAllTopics, Topic, SingleTopic, CreateTopicRequest
from services import user_service


def get_all_topics(search: str | None, category_id: int | None,
                   author_id: int | None, is_locked: bool | None,
                   user_id: int, limit: int, offset: int) -> list[ViewAllTopics]:
    """
    Retrieve all topics based on the provided filters.

     Parameters:
        search (str | None): A search term to filter topics by title.
        category_id (int | None): The ID of the category to filter topics.
        author_id (int | None): The ID of the author to filter topics.
        is_locked (bool | None): The lock status to filter topics.
        user_id (int): The ID of the user requesting the topics.
        limit (int): The maximum number of topics to return.
        offset (int): The number of topics to skip before starting to return results.

    Returns:
        list[ViewAllTopics]: A list of topics matching the filters.
    """

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
    """
    Build the WHERE conditions and parameters for the SQL query based on the provided filters.

    Parameters:
        search (str | None): A search term to filter topics by title.
        category_id (int | None): The ID of the category to filter topics.
         author_id (int | None): The ID of the author to filter topics.
         is_locked (bool | None): The lock status to filter topics.
        user_id (int): The ID of the user requesting the topics.

    Returns:
         tuple: A tuple containing the list of WHERE conditions and the list of parameters.
    """
    where_conditions = []
    params = []

    # check if user is not admin
    if not user_service.is_admin(user_id):
        where_conditions.append("""(c.is_private = 0 OR (c.is_private = 1 AND EXISTS (SELECT 1 FROM category_accesses ca WHERE ca.category_id = t.category_id AND ca.user_id = ?)))""")
        params.append(user_id)

    # check for optional parameters
    if search is not None:
        where_conditions.append("t.title like ?")
        params.append(f"%{search}%")

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
    """
    Build the final SQL query with the provided base query, conditions, and parameters.

    Parameters:
         base_query (str): The base SQL query.
        where_conditions (list): A list of WHERE conditions to apply.
        params (list): A list of parameters for the SQL query.
        limit (int): The maximum number of records to return.
        offset (int): The number of records to skip before starting to return results.

    Returns:
        tuple: A tuple containing the final SQL query and the list of parameters.
    """
    where_clause = " WHERE " + " AND ".join(where_conditions) if where_conditions else ""
    final_query = f"{base_query}{where_clause} GROUP BY t.id LIMIT ? OFFSET ?"
    params.append(limit)
    params.append(offset)

    return final_query, params


def sort_topics(topics: list[ViewAllTopics],
                reverse=False) -> list[ViewAllTopics]:
    """
    Sort a list of topics by their creation date.

    Parameters:
        topics (list[ViewAllTopics]): The list of topics to sort.
        reverse (bool): Whether to sort in descending order. Defaults to False.

    Returns:
        list[ViewAllTopics]: The sorted list of topics.
    """

    return sorted(topics,  key=lambda t: t.created_at, reverse=reverse)


def get_by_id_with_replies(topic_id: int) -> SingleTopic | None:
    """
    Retrieve a topic by its ID along with its replies.

    Parameters:
        topic_id (int): The ID of the topic to retrieve.

    Returns:
        SingleTopic | None: The SingleTopic object containing the topic and its replies if found, otherwise None.
    """
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
    """
    Create a Reply object from a database row.

    Parameters:
        row: The database row containing reply data.

    Returns:
        Reply: The Reply object created from the row data.
    """
    reply_data = row[8:]
    reply = Reply.from_query_result(*reply_data)
    reply.vote_count = int(row[14])

    return reply


def get_by_id(topic_id: int) -> Topic | None:
    """
    Retrieve a topic by its ID.

    Parameters:
        topic_id (int): The ID of the topic to retrieve.

    Returns:
        Topic | None: The Topic object if found, otherwise None.
    """
    query = """SELECT id, title, content, is_locked, category_id, created_at, best_reply_id, author_id
                FROM topics
                WHERE id = ?"""

    topic_data = read_query(query, (topic_id,))
    if not topic_data:
        return None

    return Topic.from_query_result(*topic_data[0])


def create(topic: CreateTopicRequest, user_id: int) -> Topic:
    """
    Create a new topic.

    Parameters:
        topic (CreateTopicRequest): The topic data to create.
        user_id (int): The ID of the user creating the topic.

    Returns:
        Topic: The created Topic object.
    """
    query = """INSERT INTO topics(title, content, is_locked, category_id, author_id)
                VALUES(?, ?, ?, ?, ?)"""

    params = [topic.title, topic.content, topic.is_locked, topic.category_id, user_id]

    generated_id = insert_query(query, (*params,))

    return get_by_id(generated_id)


def id_exists(topic_id: int) -> bool:
    """
    Check if a topic exists by its ID.

    Parameters:
        topic_id (int): The ID of the topic to check.

    Returns:
        bool: True if the topic exists, otherwise False.
    """
    query = """SELECT 1 
                FROM topics 
                WHERE id = ?"""

    result = read_query(query, (topic_id,))

    return len(result) > 0


def change_topic_lock_status(topic_id: int, locked_status_code: bool) -> None:
    """
    Change the lock status of a topic.

    Parameters:
        topic_id (int): The ID of the topic to update.
        locked_status_code (bool): The new lock status code to set.

    Returns:
        None
    """
    query = """UPDATE topics 
                SET is_locked = ? 
                WHERE id = ?"""

    update_query(query, (locked_status_code, topic_id))


def validate_topic_author(topic_id: int, user_id: int) -> bool:
    """
    Validate if a user is the author of a topic.

    Parameters:
        topic_id (int): The ID of the topic to check.
        user_id (int): The ID of the user to validate.

    Returns:
        bool: True if the user is the author of the topic, otherwise False.
    """
    query = """SELECT 1 
                FROM topics 
                WHERE id = ? AND author_id = ?"""

    result = read_query(query, (topic_id, user_id))

    return len(result) > 0


def update_best_reply(topic_id: int, reply_id: int, prev_best_reply: int | None) -> None:
    """
    Update the best reply for a topic.

    Parameters:
        topic_id (int): The ID of the topic to update.
        reply_id (int): The ID of the new best reply.
        prev_best_reply (int | None): The ID of the previous best reply, if any.

    Returns:
        None
    """
    if prev_best_reply is not None:
        _mark_reply_as_not_best(prev_best_reply)

    _update_topic_best_reply(topic_id, reply_id)
    _mark_reply_as_best(reply_id)


def get_topic_best_reply(topic_id: int) -> int | None:
    """
    Retrieve the best reply ID for a topic.

    Parameters:
        topic_id (int): The ID of the topic to retrieve the best reply for.

    Returns:
        int | None: The ID of the best reply if found, otherwise None.
    """
    query = """SELECT best_reply_id 
                FROM topics 
                WHERE id = ?"""

    result = read_query(query, (topic_id,))
    if not result:
        return None

    return result[0][0]


def _mark_reply_as_not_best(reply_id: int) -> None:
    """
    Mark a reply as not the best reply.

    Parameters:
        reply_id (int): The ID of the reply to update.

    Returns:
        None
    """
    query = """UPDATE replies 
                SET is_best_reply = False 
                WHERE id = ?"""

    update_query(query, (reply_id,))


def _update_topic_best_reply(topic_id: int, reply_id: int) -> None:
    """
    Update the best reply ID for a topic.

    Parameters:
        topic_id (int): The ID of the topic to update.
        reply_id (int): The ID of the new best reply.

    Returns:
        None
    """
    query = """UPDATE topics 
                SET best_reply_id = ? 
                WHERE id = ?"""

    update_query(query, (reply_id, topic_id))


def _mark_reply_as_best(reply_id: int) -> None:
    """
    Mark a reply as the best reply.

    Parameters:
        reply_id (int): The ID of the reply to update.

    Returns:
        None
    """
    query = """UPDATE replies 
                SET is_best_reply = True 
                WHERE id = ?"""

    update_query(query, (reply_id,))


def get_authors_of_topics(topics: list[ViewAllTopics]) -> dict[int, str]:
    """
    Retrieve the authors of a list of topics.

    Parameters:
        topics (list[ViewAllTopics]): The list of topics to retrieve the authors for.

    Returns:
        dict[int, str]: A dictionary mapping topic IDs to their usernames.
    """
    topic_ids = [topic.id for topic in topics]

    if not topic_ids:
        return {}

    placeholders = ", ".join("?" for _ in topic_ids)
    query = f"""SELECT t.id, u.username 
                FROM topics t 
                JOIN users u ON t.author_id = u.id
                WHERE t.id IN ({placeholders})"""

    author_data = read_query(query, tuple(topic_ids))

    return {topic_id: username for topic_id, username in author_data}


def get_categories_of_topics(topics: list[ViewAllTopics]) -> dict[int, str]:
    """
    Retrieve the categories of a list of topics.

    Parameters:
        topics (list[ViewAllTopics]): The list of topics to retrieve the categories for.

    Returns:
        dict[int, str]: A dictionary mapping topic IDs to their category titles.
    """
    topic_ids = [topic.id for topic in topics]

    if not topic_ids:
        return {}

    placeholders = ", ".join("?" for _ in topic_ids)
    query = f"""SELECT t.id, c.title 
                FROM topics t 
                JOIN categories c ON t.category_id = c.id
                WHERE t.id IN ({placeholders})"""

    category_data = read_query(query, tuple(topic_ids))

    return {topic_id: title for topic_id, title in category_data}
