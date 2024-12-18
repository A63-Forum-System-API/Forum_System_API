from starlette.responses import Response

from common.auth import get_password_hash
from data.database import insert_query, read_query


def get_conversation(conversation_id: int, order: str = "asc") -> list[dict]:
    """
    Retrieve messages for a given conversation ID, ordered by the message sent time.

    Parameters:
        conversation_id (int): The ID of the conversation.
        order (str): The order in which to sort the messages (asc or desc).

    Returns:
        list[dict]: A list of messages with text, sent time, sender's first name and picture
    """
    query = f"""
            SELECT m.text, m.sender_id, u.first_name, m.sent_at, u.picture
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
            "from_id": message[1],
            "from": message[2],
            "sent_at": message[3],
            "picture": message[4]
        })

    return messages


def get_conversation_id(user1_id: int, user2_id: int) -> int | None:
    """
    Retrieve the conversation ID for the given user IDs.

    Parameters:
        user1_id (int): The ID of the first user.
        user2_id (int): The ID of the second user.

    Returns:
        int | None: The ID of the conversation between the two users, or None if no conversation exists.
    """
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


def get_conversations(user_id: int, order="asc") -> list[dict]:
    """
    Retrieve all conversations for a given user ID, ordered by the last message sent time.

    Parameters:
        user_id (int): The ID of the user.
        order (str): The order in which to sort the conversations (asc or desc).

    Returns:
        list[dict]: A list of conversations with conversation ID, username, first name, last message, and sent time.
    """
    query = f"""
            SELECT DISTINCT c.id AS conversation_id,
                   CASE 
                       WHEN c.user1_id = ? THEN u2.id 
                       ELSE u1.id 
                   END AS user_id,
                   CASE 
                       WHEN c.user1_id = ? THEN u2.first_name 
                       ELSE u1.first_name 
                   END AS first_name,
                   CASE 
                       WHEN c.user1_id = ? THEN u2.picture 
                       ELSE u1.picture
                   END AS picture,
                   m.text AS last_message,
                   m.sent_at AS last_sent_at
            FROM conversations c
            JOIN users u1 ON c.user1_id = u1.id
            JOIN users u2 ON c.user2_id = u2.id
            JOIN messages m ON c.id = m.conversation_id
            WHERE m.sent_at = (
                SELECT MAX(m2.sent_at)
                FROM messages m2
                WHERE m2.conversation_id = c.id
            )
            AND (c.user1_id = ? OR c.user2_id = ?)
            ORDER BY m.sent_at {order}
            """

    result = read_query(query, (user_id, user_id, user_id, user_id, user_id))
    conversations = []
    for conversation in result:
        conversations.append({
            "conversation_id": conversation[0],
            "user_id": conversation[1],
            "with": f"{conversation[2]}",
            "picture": None if conversation[3] == 1 else f"{conversation[3]}",
            "last_message": conversation[4],
            "sent_at": conversation[5],
        })

    return conversations


def _get_last_message(conversation_id: int) -> tuple | None:
    """
    Retrieve the last message for a given conversation ID.

    Parameters:
        conversation_id (int): The ID of the conversation.

    Returns:
        tuple | None: A tuple containing the text and sent time of the last message, or None if no messages are found.
    """
    query = """
            SELECT text, sent_at
            FROM messages
            WHERE conversation_id = ?
            ORDER BY sent_at DESC
            LIMIT 1
            """
    result = read_query(query, (conversation_id,))
    return result[0] if result else None
