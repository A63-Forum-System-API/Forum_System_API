from starlette.responses import Response

from common.auth import get_password_hash
from data.database import insert_query, read_query
from schemas.message import Message
from services import conversation_service
from services.user_service import get_user_by_id


def create(message: Message, receiver_id: int, sender_id: int) -> str:
    """
    Create a new message.

    Parameters:
        message (Message): The message to be sent.
        receiver_id (int): The ID of the receiver.
        sender_id (int): The ID of the sender.

    Returns:
        str: A confirmation message indicating the message was sent successfully.
    """
    conversation_id = _get_conversation_id(sender_id, receiver_id)

    query = """
            INSERT INTO messages(text, sender_id, receiver_id, conversation_id)
            VALUES(?, ?, ?, ?)
            """
    insert_query(query, (message.text, sender_id, receiver_id, conversation_id))
    first_name = get_user_by_id(receiver_id).first_name

    return f"The message to {first_name} was sent successfully!"


def _get_conversation_id(user1_id: int, user2_id: int) -> int:
    """
     Retrieve or create a conversation ID for the given user IDs.

     Parameters:
         user1_id (int): The ID of the first user.
         user2_id (int): The ID of the second user.

     Returns:
         int: The ID of the conversation between the two users.
     """
    result = conversation_service.get_conversation_id(user1_id, user2_id)

    if not result:
        query = """
                INSERT INTO conversations(user1_id, user2_id)
                VALUES(?, ?)
                """
        insert_query(query, (user1_id, user2_id))

        select_query = """
                    SELECT id
                    FROM conversations
                    WHERE (user1_id = ? AND user2_id = ?)
                    OR (user1_id = ? AND user2_id = ?)
                """
        result = read_query(select_query, (user1_id, user2_id, user2_id, user1_id))
        result = result[0][0]

    return result
