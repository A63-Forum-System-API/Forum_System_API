from fastapi import APIRouter, Request, Query, Depends
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates
from common.auth import get_current_user
from services import category_service

categories_router = APIRouter(prefix='/categories')
templates = Jinja2Templates(directory='templates')


@categories_router.get("/")
def get_categories(
        request: Request,
        search: str = Query(default=""),
):
    try:
        token = request.cookies.get("token")
        if not token:
            return RedirectResponse(
                url="/?error=not_authorized_categories",
                status_code=302
            )

        try:
            current_user_id = get_current_user(token)

        except:
            return RedirectResponse(
                url="/?error=invalid_token",
                status_code=302
            )


        categories = category_service.get_categories(
            search=search,
            sort="asc",
            sort_by="title",
            limit=100,
            offset=0,
            current_user_id=current_user_id
        )

        return templates.TemplateResponse(
            request=request, name='categories.html',
            context={
                "categories": categories,
                "search": search
            }
        )

    except Exception as e:
        return templates.TemplateResponse(
            request=request, name="categories.html",
            context={
                "error": "Oops! Something went wrong while loading categories 🙈",
                "categories": [],
                "search": search
            }
        )
