from common.auth import get_password_hash
from data.database import insert_query, read_query
from schemas.user import UserCreate, User, UserUpdate


def is_admin(user_id: int):
    query = """SELECT is_admin FROM users WHERE id = ?"""
    result = read_query(query, (user_id,))

    return True if result[0][0] else False


def id_exists(user_id: int):
    query = """SELECT id FROM users WHERE id = ?"""
    result = read_query(query, (user_id,))

    return True if result else False


# def get_by_username(username: str):
#     query = """
#             SELECT id, username, first_name, last_name, email, is_admin, picture
#             FROM users WHERE username = ?
#             """
#     result = read_query(query, (username,))
#
#     if not result:
#         return None
#     result = result[0]
#
#     return User(
#         username=result[1],
#         first_name=result[2],
#         last_name=result[3],
#         email=result[4],
#         picture=result[5]
#     )

def get_user_by_id(user_id: int):
    query = """
            SELECT username, first_name, last_name, email, picture
            FROM users WHERE id = ?
            """
    result = read_query(query, (user_id,))

    return User(username=result[0][0],
                first_name=result[0][1],
                last_name=result[0][2],
                email=result[0][3],
                picture=result[0][4]
                )


def check_if_email_exist(email: str):
    query = """
            SELECT id, username, first_name, last_name, email, is_admin, picture 
            FROM users WHERE email = ?
            """
    result = read_query(query, (email,))

    if not result:
        return False
    return True


def create(user: UserCreate):
    hash_password = get_password_hash(user.password)
    query = """
            INSERT INTO users(username, first_name, last_name, email, hash_password, picture)
            VALUES(?, ?, ?, ?, ?, ?)
            """
    insert_query(query, (user.username, user.first_name,
                         user.last_name, user.email, hash_password,
                         user.picture))

    return User(username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                picture=user.picture
                )


def update(user_id: int, user: UserUpdate):
    query = """
            UPDATE users
            SET is_admin = ?
            WHERE id = ?
            """
    insert_query(query, (user.is_admin, user_id))

    return {"msg": f"User with #ID {user_id} successfully updated to {'admin' if user.is_admin else 'basic bitch!'}"}


# TODO !!! Responds with a list of all users for a specific Private Category along with their Access Level