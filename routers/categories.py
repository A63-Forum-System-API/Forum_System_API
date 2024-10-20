from fastapi import APIRouter, Response, Depends, HTTPException
from pydantic import BaseModel
from schemas.category import Category
from services import category_service, user_service
from common.auth import get_current_user
from starlette import status


categories_router = APIRouter(prefix="/categories")


@categories_router.get("/")
def get_all_categories(
    sort: str | None = None,
    sort_by: str | None = None,
    search: str | None = None,
    limit: int = 10,
    offset: int = 0,
    current_user_id: int = Depends(get_current_user),
):
    # validation
    if not sort in (None, "asc", "desc"):
        return Response(
            content=f"Invalid value for sort: {sort}. Valid values are: asc, desc",
            status_code=400,
        )
    if sort and sort_by not in ("title", "created_at"):
        return Response(
            content=f"Invalid value for sort_by: {sort_by}. Valid values are: title, created_at",
            status_code=400,
        )
    if limit < 1 or limit > 100:  # fastapi checks if limit is int
        return Response(
            content=f"Invalid value for limit: {limit}. Valid values are: int [1-100]",
            status_code=400,
        )
    if offset < 0:
        return Response(
            content=f"Invalid value for offset: {offset}. Valid values are: int >= 0",
            status_code=400,
        )

    return category_service.get_categories(
        search, sort, sort_by, limit, offset, current_user_id
    )


@categories_router.get("/{id}")
def get_category_by_id(id: int, current_user_id: int = Depends(get_current_user)):
    try:
        category = category_service.get_by_id_with_topics(id, current_user_id)
    except Exception as e:
        return Response(content=str(e), status_code=403)

    if category is None:
        return Response(content=f"No category with ID {id} found", status_code=404)
    else:
        return category


@categories_router.post("/", status_code=201)
def create_category(
    category: Category, current_user_id: int = Depends(get_current_user)
):
    if not user_service.is_admin(current_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to create categories!",
        )
    try:
        return category_service.create(category, current_user_id)
    except Exception as e:
        return Response(content=str(e), status_code=409)


@categories_router.put("/{id}/private/{private_status_code}", status_code=204)
def change_category_private_status(
    id: int, private_status_code: int, current_user_id: int = Depends(get_current_user)
):
    if not user_service.is_admin(current_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to update categories!",
        )
    if private_status_code not in (0, 1):
        return Response(content="Private status code must be 0 or 1", status_code=400)

    try:
        category_service.change_category_private_status(id, private_status_code)
        return Response(status_code=204)
    except Exception as e:
        return Response(content=str(e), status_code=404)


@categories_router.put("/{id}/lock/{locked_status_code}", status_code=204)
def change_category_lock_status(
    id: int, locked_status_code: int, current_user_id: int = Depends(get_current_user)
):
    if not user_service.is_admin(current_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to update categories!",
        )
    if locked_status_code not in (0, 1):
        return Response(content="Locked status code must be 0 or 1", status_code=400)

    try:
        category_service.change_category_lock_status(id, locked_status_code)
        return Response(status_code=204)
    except Exception as e:
        return Response(content=str(e), status_code=404)


@categories_router.put("/{category_id}/users/{user_id}/", status_code=204)
def manage_user_access_to_private_category(
    category_id: int,
    user_id: int,
    code_read_access: int,
    code_write_access: int,
    current_user_id: int = Depends(get_current_user),
):
    if not user_service.is_admin(current_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to add users!",
        )
    if code_read_access not in (0, 1) or code_write_access not in (0, 1):
        return Response(
            content="Write and read access code must be 0 or 1", status_code=400
        )
    try:
        category_service.manage_user_access_to_private_category(
            category_id, user_id, code_read_access, code_write_access
        )
        return Response(status_code=204)

    except Exception as e:
        return Response(content=str(e), status_code=404)


@categories_router.get("/{category_id}/private/users")
def get_privileged_users_by_category(
    category_id: int, current_user_id: int = Depends(get_current_user)
):
    if not user_service.is_admin(current_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to view privileged users!",
        )
    try:
        return category_service.get_privileged_users_by_category(category_id)
    except Exception as e:
        return Response(content=str(e), status_code=404)
