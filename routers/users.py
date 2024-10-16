from fastapi import APIRouter, Depends
from fastapi.openapi.models import Response
from fastapi.security import OAuth2PasswordRequestForm

from common.auth import authenticate_user, create_access_token
from schemas.reply import ReplyBase
from schemas.token import Token
from schemas.user import UserCreate, UserLogIn
from services import topic_service, reply_service, user_service

users_router = APIRouter(prefix='/users')


@users_router.post('/register', status_code=201)
def create_user(user: UserCreate):
    existing_user = user_service.get_by_username(user.username)
    if existing_user:
        return Response(content=f"User with username {user.username} already exists", status_code=409)

    return user_service.create(user)


@users_router.post('/login')
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)

    if not user:
        return Response(content="User not found", status_code=404)

    access_token = create_access_token(data=user)
    return Token(access_token=access_token,
                 token_type='bearer')

