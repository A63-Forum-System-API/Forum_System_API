from data.database import read_query


def id_exists(reply_id: int):
    query = """SELECT 1 
                FROM replies 
                WHERE id = ?"""
    result = read_query(query, (reply_id,))

    return len(result) > 0