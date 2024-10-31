from fastapi import APIRouter, Request, Form
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates
from common.auth import get_current_user
from schemas.message import Message
from services import user_service, message_service

messages_router = APIRouter(prefix='/messages')
templates = Jinja2Templates(directory='templates')


@messages_router.post('/')
def create_new_message(
        request: Request,
        message: str = Form(...),
        username: str = Form(...)):

    try:
        token = request.cookies.get("token")
        if not token:
            return RedirectResponse(
                url="/?error=not_authorized",
                status_code=302
            )

        current_user_id = get_current_user(token)

        receiver_user = user_service.get_user_by_username(username)
        if not receiver_user:
            return templates.TemplateResponse(
                request=request, name="conversations.html",
                context={
                    "error": f"User '{username}' not found!"
                }
            )

        message = Message(text=message)
        message_service.create(message, receiver_user["id"], current_user_id)

        return RedirectResponse(
            url=f"/conversations/{receiver_user["id"]}",
            status_code=302
        )

    except Exception:
        return templates.TemplateResponse(
            request=request, name="conversations.html",
            context={
                "error": "Oops! Something went wrong while loading conversations 🙈",
            }
        )