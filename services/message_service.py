from starlette.responses import Response

from common.auth import get_password_hash
from data.database import insert_query, read_query
from schemas.message import Message
from services.user_service import get_user_by_id


def create(message: Message, receiver_id: int, sender_id: int):
    conversation_id = _get_conversation_id(sender_id, receiver_id)

    query = """
            INSERT INTO messages(text, sender_id, receiver_id, conversation_id)
            VALUES(?, ?, ?, ?)
            """
    insert_query(query, (message.text, sender_id, receiver_id, conversation_id))
    first_name = get_user_by_id(sender_id).first_name

    return Response(content=f"The message to {first_name} was sent successfully!", status_code=201)


def _get_conversation_id(user1_id, user2_id):
    if user1_id == user2_id:
        query = """
                    SELECT id FROM conversations
                    WHERE user1_id = ? AND user2_id = ?
                    """
        result = read_query(query, (user1_id, user2_id))
    else:
        query = """
                    SELECT id FROM conversations
                    WHERE (user1_id = ? AND user2_id = ?)
                    OR (user1_id = ? AND user2_id = ?)
                    """
        result = read_query(query, (user1_id, user2_id, user2_id, user1_id))

    if not result:
        query = """
                    INSERT INTO conversations(user1_id, user2_id)
                    VALUES(?, ?)
                    """
        insert_query(query, (user1_id, user2_id))

        result = read_query(query,
                            (user1_id, user2_id) if user1_id == user2_id
                            else (user1_id, user2_id, user2_id, user1_id))

    return result[0][0]
