from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

index_router = APIRouter(prefix='')
templates = Jinja2Templates(directory='templates')

@index_router.get('/')
def index(request: Request,
          error: str | None = None):
    error_messages = {
        "not_authorized_categories": "You need to login to view categories!",
        "invalid_token": "Your sesh has expired! Please login again!"
    }
    return templates.TemplateResponse(
        request=request, name='index.html',
        context={'error': error_messages.get(error)})