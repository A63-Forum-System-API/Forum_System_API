from data.database import insert_query
from schemas.topic import TopicCreate


def create(topic: TopicCreate):
    is_locked_bool = True if topic.is_locked == 'locked' else False

    # TODO take id of user who is logged in
    author_id = 0

    query = """INSERT INTO topics(title, content, is_locked, category_id, author_id)
                VALUES(?, ?, ?, ?)"""
    params = [topic.title, topic.content, is_locked_bool, topic.category_id, author_id]

    generated_id = insert_query(query, params)
    topic.id = generated_id

    return topic
