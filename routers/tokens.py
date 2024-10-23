from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from common.auth import authenticate_user, create_access_token
from schemas.token import Token

token_router = APIRouter(prefix='/token', tags=['Token'])


@token_router.post('/')
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"})

    access_token = create_access_token(data=user)
    return Token(access_token=access_token,
                 token_type='bearer')
