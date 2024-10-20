from starlette.responses import Response

from common.auth import get_password_hash
from data.database import insert_query, read_query


def get_conversation(conversation_id: int, order: str = "asc"):
    query = f"""
            SELECT m.text, m.sender_id, u.first_name, m.sent_at
            FROM messages m
            JOIN users u ON m.sender_id = u.id
            WHERE m.conversation_id = ?
            ORDER BY m.sent_at {order}
            """
    result = read_query(query, (conversation_id,))
    messages = []
    for message in result:
        messages.append({
            "text": message[0],
            "from": message[2],
            "sent_at": message[3],
        })

    return messages


def get_conversation_id(user1_id: int, user2_id: int) -> int | None:
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

    return result[0][0] if result else None