import mariadb
from fastapi import APIRouter, Request, Form
from pydantic import ValidationError
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates
from common.auth import authenticate_user, create_access_token
from schemas.user import UserCreate
from services import user_service

users_router = APIRouter(prefix='/users')
templates = Jinja2Templates(directory='templates')

@users_router.post('/login')
def login(request: Request,
          username: str = Form(...),
          password: str = Form(...)):
    user = authenticate_user(username, password)

    if not user:
        return templates.TemplateResponse(
            request=request, name='index.html', context={'error': 'Invalid login data'})

    else:
        access_token = create_access_token(data=user)
        response = RedirectResponse(url='/', status_code=302)
        response.set_cookie('token', access_token)
        return response


@users_router.post('/logout')
def logout():
    response = RedirectResponse(url='/', status_code=302)
    response.delete_cookie('token')
    return response

@users_router.get('/register')
def serve_register(request: Request):
    return templates.TemplateResponse(request=request, name='register.html')


@users_router.post('/register')
def register(request: Request,
             username: str = Form(...),
             first_name: str = Form(...),
             last_name: str = Form(...),
             email: str = Form(...),
             password: str = Form(...)):

    try:
        user_data = UserCreate(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password
        )
    except ValidationError as e:
        return templates.TemplateResponse(
            request=request,
            name='register.html',
            context={'error': f"{e.errors()[0]['loc'][0]}: {e.errors()[0]['msg']}"}
        )

    try:
        user_service.create(user_data)
        user = authenticate_user(username, password)
        token = create_access_token(data=user)
        response = RedirectResponse(url='/', status_code=302)
        response.set_cookie('token', token)
        return response

    except mariadb.IntegrityError as e:
        error_message = ""
        if "username_UNIQUE" in str(e):
            error_message = f"User with username '{username}' already exists"
        elif "email_UNIQUE" in str(e):
            error_message = f"User with email '{email}' already exists"
        else:
            error_message = "Registration failed. Please try again."

        return templates.TemplateResponse(
            request=request,
            name='register.html',
            context={'error': error_message}
        )

@users_router.get("/logout")
def logout():
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("token")
    return response