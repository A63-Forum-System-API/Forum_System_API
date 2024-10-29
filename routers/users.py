from typing import Optional, Literal, Union

import mariadb
from fastapi import APIRouter, Depends, HTTPException, Path, Query, UploadFile, File
from fastapi.openapi.models import Response
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from common.auth import authenticate_user, create_access_token
from common.custom_responses import AlreadyExists, InternalServerError, Unauthorized, OnlyAdminAccess, NotFound, \
    BadRequest, ForbiddenAccess, OK
from schemas.token import Token
from schemas.user import UserCreate, UserLogIn, UserUpdate, UserUpdate
from services import topic_service, reply_service, user_service
from common.auth import get_current_user


users_router = APIRouter(prefix="/users", tags=["Users"])


@users_router.post("/register", status_code=201)
def create_user(user: UserCreate):
    """
    Create a new user.

    Parameters:
        user (UserCreate): The user data for creating a new user.

    Returns:
        Response: The created user or an error response
        if the user already exists or an internal server error occurs.
    """
    try:
        return user_service.create(user)

    except mariadb.IntegrityError as e:
        if "username_UNIQUE" in str(e):
            return AlreadyExists(f"User with username '{user.username}'")

        elif "email_UNIQUE" in str(e):
            return AlreadyExists(f"User with email '{user.email}'")

        else:
            return InternalServerError()


# TODO add logout
@users_router.post('/login')
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate the user and return an access token.

    Parameters:
        form_data (OAuth2PasswordRequestForm): The form data containing the username and password.

    Returns:
        Token: An access token if authentication is successful, or an Unauthorized response if authentication fails.
    """
    user = authenticate_user(form_data.username, form_data.password)

    if not user:
        return Unauthorized("Invalid username or password")

    access_token = create_access_token(data=user)
    return Token(access_token=access_token,
                 token_type='bearer')


@users_router.put('/{user_id}')
def update_user(user_id: int,
                is_admin: bool = Query(description="is_admin must be either false (not admin) or true (admin)"),
                current_user_id: int = Depends(get_current_user)):
    """
     Update the admin status of a user.

     Parameters:
         user_id (int): The ID of the user to be updated.
         is_admin (bool): The new admin status (true for admin, false for not admin).
         current_user_id (int): The ID of the current user (retrieved from the authentication dependency).

     Returns:
         Response: A confirmation message indicating the user status was updated successfully,
         or an error response if the current user is not an admin, the user ID does not exist,
         the user is trying to update their own status, or the user to be updated is already an admin.
     """

    if not user_service.is_admin(current_user_id):
        return OnlyAdminAccess("update user status")

    if not user_service.id_exists(user_id):
        return NotFound(f"User ID: {user_id}")

    if user_id == current_user_id and user_id != 1:
        return BadRequest("You are not allowed to update your own user status")

    if user_service.is_admin(user_id) and current_user_id != 1:
        return ForbiddenAccess("This user is already an admin")

    return user_service.update(user_id, is_admin)

#
# @users_router.put("/{user_id}/picture")
# def update_user_picture(user_id: int, picture: Union[UploadFile, None] = File(None)):
#     if picture is None:
#         return BadRequest("No picture provided")
#
#     picture_content = picture.file.read()
#
#     compressed_picture_content = compress_image(picture_content)
#
#     # Call the service function to update the user picture in the database
#     update_user_picture(user_id, compressed_picture_content)
#
#     return OK("Profile picture updated")

