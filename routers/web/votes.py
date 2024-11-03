from fastapi import APIRouter, Request, Form
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from common.auth import get_current_user
from services import reply_service, topic_service, vote_service

votes_router = APIRouter(prefix='/votes')
templates = Jinja2Templates(directory='templates')

@votes_router.post("/{reply_id}")
def handle_vote(
    request: Request,
    reply_id: int,
    vote_type: str = Form(...),
):
    try:
        token = request.cookies.get("token")
        if not token:
            return RedirectResponse(
                url=f"/?error=not_authorized",
                status_code=302
            )

        try:
            current_user_id = get_current_user(token)
        except:
            return RedirectResponse(
                url=f"/topics/{reply_id}?error=invalid_token",
                status_code=302
            )

        reply = reply_service.get_by_id(reply_id)

        vote = vote_service.get_vote(reply_id, current_user_id)
        vote_type_value = 1 if vote_type == "upvote" else 0

        if vote is None:
            vote_service.create_vote(reply_id, vote_type_value, current_user_id)
        elif vote != vote_type_value:
            vote_service.update_vote(reply_id, vote_type_value, current_user_id)
        else:
            vote_service.delete_vote(reply_id, current_user_id)

        return RedirectResponse(
            url=f"/topics/{reply.topic_id}",
            status_code=302
        )

    except Exception as e:
        print(f"Vote error: {str(e)}")
        return RedirectResponse(
            url=f"/topics/{reply.topic_id}?error=something_went_wrong",
            status_code=302
        )