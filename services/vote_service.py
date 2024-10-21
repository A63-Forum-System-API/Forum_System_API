from data.database import read_query, insert_query, update_query


def exists(reply_id: int, user_id: int):
    query = """SELECT vote_type 
                FROM votes 
                WHERE reply_id = ? AND user_id = ?"""
    result = read_query(query, (reply_id, user_id))

    return result[0][0] if result else None


def create_vote(reply_id: int, vote_type: int, user_id: int):
    vote_type = True if vote_type == 1 else False

    query = """INSERT INTO votes(reply_id, vote_type, user_id)
                VALUES(?, ?, ?)"""
    params = [reply_id, vote_type, user_id]

    insert_query(query, (*params,))


def update_vote(reply_id: int, vote_type: int, user_id: int):
    vote_type = True if vote_type == 1 else False

    query = """UPDATE votes 
                SET vote_type = ? 
                WHERE reply_id = ? AND user_id = ?"""
    update_query(query, (vote_type, reply_id, user_id))

