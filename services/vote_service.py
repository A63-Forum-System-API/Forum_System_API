from data.database import read_query


def exists(reply_id: int, user_id: int):
    query = """SELECT 1 
                FROM votes 
                WHERE reply_id = ? AND user_ud = ?"""
    result = read_query(query, (reply_id, user_id))

    return len(result) > 0

def create_vote(reply_id: int, vote_type: str, user_id: int):
    vote_type = True if vote_type == 'upvote' else False

    query = """INSERT INTO votes(reply_id, vote_type, user_id)
                VALUES(?, ?, ?)"""
    params = [reply_id, vote_type, user_id]

    read_query(query, (*params,))

def update_vote(reply_id: int, vote_type: str, user_id: int):
    vote_type = True if vote_type == 'upvote' else False

    query = """UPDATE votes 
                SET vote_type = ? 
                WHERE reply_id = ? AND user_id = ?"""
    read_query(query, (vote_type, reply_id, user_id))

