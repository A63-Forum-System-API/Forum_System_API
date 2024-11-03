from fastapi import APIRouter, Request, Form
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from common.auth import get_current_user
from schemas.reply import Reply, CreateReplyRequest
from services import reply_service, topic_service, vote_service

replies_router = APIRouter(prefix='/replies')
templates = Jinja2Templates(directory='templates')

@replies_router.post("/{topic_id}")
def handle_vote(
    request: Request,
    topic_id: int,
    content: str = Form(...),
):
    try:
        token = request.cookies.get("token")
        if not token:
            return RedirectResponse(
                url=f"/?error=not_authorized",
                status_code=302
            )

        current_user_id = get_current_user(token)

        request_reply = CreateReplyRequest(content=content, topic_id=topic_id)
        reply = reply_service.create(request_reply, current_user_id)


        return RedirectResponse(
            url=f"/topics/{topic_id}",
            status_code=302
        )

    except Exception as e:
        print(f"Vote error: {str(e)}")
        return RedirectResponse(
            url=f"/topics/{topic_id}?error=something_went_wrong",
            status_code=302
        )