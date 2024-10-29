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
    """
    Check if a user is an admin.

    Parameters:
        user_id (int): The ID of the user.

    Returns:
        bool: True if the user is an admin, False otherwise.
    """
    query = """SELECT is_admin FROM users WHERE id = ?"""
    result = read_query(query, (user_id,))

    return True if result[0][0] else False


def id_exists(user_id: int) -> bool:
    """
    Check if a user ID exists in the users table.

    Parameters:
        user_id (int): The ID of the user.

    Returns:
        bool: True if the user ID exists, False otherwise.
    """
    query = """SELECT id FROM users WHERE id = ?"""
    result = read_query(query, (user_id,))

    return True if result else False


def get_user_by_id(user_id: int) -> User:
    """
    Retrieve user details by user ID.

    Parameters:
        user_id (int): The ID of the user.

    Returns:
        User: A User object containing the user's details.
    """
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


def create(user: UserCreate) -> User:
    """
    Create a new user.

    Parameters:
        user (UserCreate): The user data for creating a new user.

    Returns:
        User: A User object containing the created user's details.
    """
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


def update(user_id: int, is_admin: bool) -> dict:
    """
    Update the admin status of a user.

    Parameters:
        user_id (int): The ID of the user to be updated.
        is_admin (bool): The new admin status (true for admin, false for not admin).

    Returns:
        dict: A confirmation message indicating the user status was updated successfully.
    """
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

