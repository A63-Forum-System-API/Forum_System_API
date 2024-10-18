from fastapi import APIRouter, Depends
from fastapi.openapi.models import Response
from common.auth import get_current_user
from services import reply_service, vote_service, category_service

votes_router = APIRouter(prefix='/votes')


@votes_router.put('/{reply_id}')
def vote(reply_id: int,
         vote_type: str,
         current_user_id: int = Depends(get_current_user)):
    vote_int = 1 if vote_type == 'upvote' else 0


    category_id = reply_service.get_category_id(reply_id)
    access = category_service.validate_user_access(current_user_id, category_id)
    if access.write_access:
        return Response(content="User does not have access to write a reply to this topic", status_code=403)

    if not reply_service.id_exists(reply_id):
        return Response(content=f"No reply with ID {reply_id} found", status_code=404)

    vote = vote_service.exists(reply_id, current_user_id)
    if vote is None:
        vote_service.create_vote(reply_id, vote_type, current_user_id)
        return Response(content=f"User voted for reply with ID {reply_id} successfully", status_code=201)

    if vote == vote_int:
        return Response(content=f"Current user has already voted for this reply with '{vote_type}'", status_code=400)

    vote_service.update_vote(reply_id, vote_type, current_user_id)
    return {'message': f'Vote is successfully changed to {vote_type}.'}
