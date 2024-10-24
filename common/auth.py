import os
from datetime import timedelta, datetime, timezone
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from dotenv import load_dotenv
from data.database import read_query
from schemas.token import TokenData


load_dotenv()

_SECRET_KEY = os.getenv("SECRET_KEY")
_ALGORITHM = os.getenv("ALGORITHM")
_ACCESS_TOKEN_EXPIRE = int(os.getenv("ACCESS_TOKEN_EXPIRE"))


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


# utility funcs
def verify_password(plain_password: str, hash_password: str):
    return pwd_context.verify(plain_password, hash_password)


def get_password_hash(password: str):
    return pwd_context.hash(password)


def authenticate_user(
        username: str,
        password: str):

    query = """SELECT id, hash_password 
                FROM users 
                WHERE username = ?"""

    user_data = read_query(query, (username,))

    if len(user_data) < 1:
        return None
    user = user_data[0]
    hash_password = user[1]
    if not verify_password(password, hash_password):
        return None

    return {"user_id": user[0]}


def create_access_token(data: dict):

    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=_ACCESS_TOKEN_EXPIRE)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, _SECRET_KEY, algorithm=_ALGORITHM)

    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme)):
    credential_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"})

    try:
        payload = jwt.decode(token, _SECRET_KEY, algorithms=[_ALGORITHM])
        user_identifier: str = payload.get("user_id")
        if user_identifier is None:
            raise credential_exception

        TokenData(user_identifier=user_identifier)

    except JWTError:
        raise credential_exception

    query = "SELECT id FROM users WHERE id = ?"
    user = read_query(query, (user_identifier,))

    if user is None:
        raise credential_exception

    return user[0][0]


