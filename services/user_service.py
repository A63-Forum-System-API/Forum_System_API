from tkinter import Image
# from PIL import Image
import io
from fastapi import UploadFile, File, HTTPException
from typing import Union

import data
from fastapi import HTTPException

from common.auth import get_password_hash
from data.database import insert_query, read_query
from schemas.user import UserCreate, User, UserUpdate


def is_admin(user_id: int) -> bool:
    query = """SELECT is_admin FROM users WHERE id = ?"""
    result = read_query(query, (user_id,))

    return True if result[0][0] else False


def id_exists(user_id: int) -> bool:
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


# def check_if_email_exist(email: str) -> bool:
#     query = """
#             SELECT id, username, first_name, last_name, email, is_admin, picture
#             FROM users WHERE email = ?
#             """
#     result = read_query(query, (email,))
#
#     if not result:
#         return False
#     return True


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


def update(user_id: int, is_admin: bool):
    query = """
            UPDATE users
            SET is_admin = ?
            WHERE id = ?
            """
    insert_query(query, (is_admin, user_id))

    return {"msg": f"User with #ID {user_id} successfully updated to {'admin' if is_admin else 'regular user!'}"}


# def compress_image(image_content: bytes, max_size_mb: int = 5) -> bytes:
#     image = Image.open(io.BytesIO(image_content))
#     if image.mode == "RGBA":
#         image = image.convert("RGB")
#     compressed_image_io = io.BytesIO()
#     quality = 85
#     while True:
#         compressed_image_io.seek(0)
#         image.save(compressed_image_io, format="JPEG", quality=quality)
#         size = compressed_image_io.tell()
#         if size <= max_size_mb * 1024 * 1024:
#             break
#         quality -= 5
#         if quality <= 0:
#             raise HTTPException(status_code=500, detail="Cannot compress the image to the required size!")
#     compressed_image_io.seek(0)
#     compressed_image_content = compressed_image_io.read()
#
#     return compressed_image_content
#
#
# def update_user_picture(user_id: int, picture: Union[UploadFile, None] = File(None)):
#     if picture is None:
#         raise HTTPException(status_code=400, detail="No picture provided!")
#     picture_content = picture.file.read()
#     compressed_picture_content = compress_image(picture_content)
#     sql = """
#             UPDATE users SET picture = ?
#             WHERE id = ?
#             """
#     data.database.insert_query(sql, (compressed_picture_content, user_id))
#     return {"message": "Profile picture updated."}

