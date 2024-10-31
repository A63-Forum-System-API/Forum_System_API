from fastapi import APIRouter, Request
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates
from common.auth import get_current_user
from services import conversation_service

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


#
# @conversations_router.get("/{receiver_id}")
# def view_conversation(receiver_id: int,
#                       order: Optional[str] = Query("asc", pattern="^(asc|desc)$"),
#                       current_user_id: int = Depends(get_current_user)):
#     """
#     View a conversation between the current user and the specified receiver.
#
#     Parameters:
#         receiver_id (int): The ID of the receiver.
#         order (Optional[str]): The order in which to sort the messages (asc or desc).
#         current_user_id (int): The ID of the current user (retrieved from the authentication dependency).
#
#     Returns:
#         Response: The conversation details or a NotFound response if the user or conversation does not exist.
#     """
#
#     if not user_service.id_exists(receiver_id):
#         return NotFound(f"User ID: {receiver_id}")
#
#     conversation_id = conversation_service.get_conversation_id(current_user_id, receiver_id)
#
#     if not conversation_id:
#         return NotFound(f"Conversation with user ID: {receiver_id}")
#
#     return conversation_service.get_conversation(conversation_id, order)
#
