from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from common.auth import get_current_user
from services import user_service

index_router = APIRouter(prefix='')
templates = Jinja2Templates(directory='templates')

@index_router.get('/')
def index(request: Request,
          error: str | None = None):
    error_messages = {
        "not_authorized_categories": "You need to login to view categories!",
        "invalid_token": "Your sesh has expired! Please login again!",
        "something_went_wrong": "Oops! Something went wrong while loading categories 🙈",
    }
    token = request.cookies.get("token")
    user = None
    if token:
        try:
            user_id = get_current_user(token)
            user = user_service.get_user_by_id(user_id)
        except:
            user = None

    return templates.TemplateResponse(
        request=request, name='index.html',
        context={'error': error_messages.get(error),
                 'first_name': user.first_name if user else None})