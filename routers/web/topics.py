from fastapi import APIRouter, Request
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from common.auth import get_current_user
from schemas.topic import CreateTopicRequest
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

@topics_router.get("/")
def get_all_toppics(
        request: Request,
        search: str | None = None,
        category_id: str | None = None,
        author_id: str | None = None,
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
            if author_id == "true":
                author_id = current_user_id

        except:
            return RedirectResponse(
                url="/?error=invalid_token",
                status_code=302
            )

        topics = topic_service.get_all_topics(user_id=current_user_id,
                                              author_id=author_id,
                                              search=search,
                                              category_id=category_id,
                                              limit=100,
                                              offset=0,
                                              is_locked=None)

        authors_of_topics = topic_service.get_authors_of_topics(topics)
        categories_of_topics = topic_service.get_categories_of_topics(topics)


        return templates.TemplateResponse(
            request=request, name='newest-topics.html',
            context={
                "topics": topics,
                "categories_of_topics": categories_of_topics,
                "authors_of_topics": authors_of_topics,
            }
        )

    except Exception:
        return templates.TemplateResponse(
            request=request, name="newest-topics.html",
            context={
                "error": "Oops! Something went wrong while loading topics 🙈",
            }
        )


from fastapi import Form

@topics_router.post("/")
async def create_topic(
        request: Request,
        title: str = Form(...),
        content: str = Form(...),
        category_id: int = Form(...)
):
    try:
        token = request.cookies.get("token")
        if not token:
            return RedirectResponse(
                url="/?error=not_authorized_topics",
                status_code=302
            )

        try:
            current_user_id = get_current_user(token)
        except Exception:
            return RedirectResponse(
                url="/?error=invalid_token",
                status_code=302
            )

        # Създаване на тема чрез сървисния слой
        topic_service.create(CreateTopicRequest(
            title=title,
            content=content,
            category_id=category_id
        ), current_user_id)

        return RedirectResponse(
            url="/topics",
            status_code=302
        )

    except Exception as e:
        return templates.TemplateResponse(
            "newest-topics.html",
            {"request": request, "error": "Oops! Something went wrong while creating topic 🙈"}
        )






