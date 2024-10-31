from data.database import read_query, insert_query, update_query, delete_query


def get_vote(reply_id: int, user_id: int) -> bool:
    """
    Retrieve the vote type for a specific reply and user.

    Parameters:
        reply_id (int): The ID of the reply to check.
        user_id (int): The ID of the user to check.

    Returns:
        bool: The vote type if found, otherwise None.
    """
    query = """SELECT vote_type 
                FROM votes 
                WHERE reply_id = ? AND user_id = ?"""
    result = read_query(query, (reply_id, user_id))

    return result[0][0] if result else None


def create_vote(reply_id: int, vote_type: int, user_id: int) -> None:
    """
    Create a new vote for a reply.

    Parameters:
        reply_id (int): The ID of the reply to vote on.
        vote_type (int): The type of vote (1 for upvote, 0 for downvote).
        user_id (int): The ID of the user casting the vote.

    Returns:
        None
    """
    vote_type = True if vote_type == 1 else False

    query = """INSERT INTO votes(reply_id, vote_type, user_id)
                VALUES(?, ?, ?)"""
    params = [reply_id, vote_type, user_id]

    insert_query(query, (*params,))


def update_vote(reply_id: int, vote_type: int, user_id: int) -> None:
    """
    Update the vote type for a specific reply and user.

    Parameters:
        reply_id (int): The ID of the reply to update the vote for.
        vote_type (int): The new vote type (1 for upvote, 0 for downvote).
        user_id (int): The ID of the user updating the vote.

    Returns:
        None
    """
    vote_type = True if vote_type == 1 else False

    query = """UPDATE votes 
                SET vote_type = ? 
                WHERE reply_id = ? AND user_id = ?"""
    update_query(query, (vote_type, reply_id, user_id))


def delete_vote(reply_id: int, user_id: int) -> None:
    """
    Delete a vote for a specific reply and user.

    Parameters:
        reply_id (int): The ID of the reply to delete the vote for.
        user_id (int): The ID of the user whose vote is to be deleted.

    Returns:
        None
    """
    query = """DELETE FROM votes 
                WHERE reply_id = ? AND user_id = ?"""

    delete_query(query, (reply_id, user_id))
