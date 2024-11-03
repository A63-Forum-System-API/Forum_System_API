from fastapi import APIRouter, Request
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from common.auth import get_current_user
from services import topic_service, category_service, user_service, reply_service

topics_router = APIRouter(prefix='/topics')
templates = Jinja2Templates(directory='templates')


@topics_router.get("/{topic_id}")
def get_topic_by_id(request: Request, topic_id: int):
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

        topic = topic_service.get_by_id_with_replies(topic_id)
        category = category_service.get_by_id(topic.topic.category_id)
        user = user_service.get_user_by_id(topic.topic.author_id)
        authors_of_replies = reply_service.get_authors_of_replies(topic.all_replies)

        return templates.TemplateResponse(
            request=request, name='single-topic.html',
            context={
                "topic": topic,
                "category_title": category.title,
                "author_username": user.username,
                "authors_of_replies": authors_of_replies,
                "topic_id": topic_id,
            }
        )

    except Exception:
        return templates.TemplateResponse(
            request=request, name="newest-topics.html",
            context={
                "error": "Oops! Something went wrong while loading conversations 🙈",
            }
        )