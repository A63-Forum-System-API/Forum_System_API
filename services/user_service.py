from common.auth import get_password_hash
from data.database import read_query
from schemas.user import User


def is_admin(user_id: int):
    query = """SELECT is_admin FROM users WHERE id = ?"""
    result = read_query(query, (user_id,))

    if len(result) < 1:
        user_is_admin = result[0][0]
        return bool(user_is_admin)

    return False


def get_by_username(username: str):
    query = """
            SELECT id, username, first_name, last_name, email, is_admin, picture 
            FROM users WHERE username = ?
            """
    result = read_query(query, (username,))

    if not result:
        return None
    result = result[0]

    return User(
        id=result[0],
        username=result[1],
        first_name=result[2],
        last_name=result[3],
        email=result[4],
        is_admin=bool(result[5]),
        picture=result[6]
    )


def create(user: User):
    hash_password = get_password_hash(user.password)
    query = """
            INSERT INTO users(username, first_name, last_name, email, hash_password, is_admin, picture)
            VALUES(?, ?, ?, ?, ?, ?, ?)
            """
    generated_id = read_query(query, (user.username, user.first_name,
                                      user.last_name, user.email, hash_password,
                                      user.is_admin, user.picture))

    return User(id=generated_id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                is_admin=user.is_admin,
                picture=user.picture
    )