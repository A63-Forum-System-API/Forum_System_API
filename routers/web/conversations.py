from fastapi import APIRouter, Request, Form
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates
from common.auth import get_current_user
from routers.api.categories import categories_router
from services import conversation_service, user_service

conversations_router = APIRouter(prefix='/conversations')
templates = Jinja2Templates(directory='templates')


@conversations_router.get('/')
def view_conversations(request: Request):
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

        conversations = conversation_service.get_conversations(current_user_id, "desc")

        return templates.TemplateResponse(
            request=request, name='conversations.html',
            context={
                "conversations": conversations
            }
        )

    except Exception as e:
        return templates.TemplateResponse(
            request=request, name="conversations.html",
            context={
                "error": "Oops! Something went wrong while loading conversations 🙈",
                "conversations": [],
            }
        )


@conversations_router.get('/count')
def get_conversations_count(request: Request):
    try:
        token = request.cookies.get("token")
        if not token:
            return {"count": 0}

        current_user_id = get_current_user(token)
        count = len(conversation_service.get_conversations(current_user_id))
        return {"count": count}

    except Exception:
        return {"count": 0}

@conversations_router.get("/{receiver_id}")
def view_conversation(request: Request,
                      receiver_id: int):

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

        conversation_id = conversation_service.get_conversation_id(current_user_id, receiver_id)
        conversation = conversation_service.get_conversation(conversation_id, "desc")
        receiver = user_service.get_user_by_id(receiver_id)
        return templates.TemplateResponse(
            request=request, name='single-conversation.html',
            context={
                "conversation": conversation,
                "receiver_id": receiver_id,
                "receiver_username": receiver.username
            }
        )

    except Exception:
        return templates.TemplateResponse(
            request=request, name="conversations.html",
            context={
                "error": "Oops! Something went wrong while loading conversations 🙈",
                "conversations": [],
            }
        )



