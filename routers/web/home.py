from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

index_router = APIRouter(prefix='')
templates = Jinja2Templates(directory='templates')

@index_router.get('/')
def index(request: Request):
    return templates.TemplateResponse(
        request=request, name='index.html')