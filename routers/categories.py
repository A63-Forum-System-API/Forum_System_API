from fastapi import APIRouter, Response
from pydantic import BaseModel
from schemas.category import Category
from services import category_service


categories_router = APIRouter(prefix='/categories')


@categories_router.get('/')
def get_all_categories(
    sort: str | None = None,
    sort_by: str | None = None,
    search: str | None = None,
    limit: int = 10,
    offset: int = 0
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
    if limit < 1 or limit > 100: # fastapi checks if limit is int
        return Response(
            content=f"Invalid value for limit: {limit}. Valid values are: int [1-100]", 
            status_code=400,
            )
    if offset < 0:
        return Response(
            content=f"Invalid value for offset: {offset}. Valid values are: int >= 0", 
            status_code=400,
            )

    return category_service.get_categories(search, sort, sort_by, limit, offset)



@categories_router.get('/{id}')
def get_category_by_id(id: int):
    category = category_service.get_by_id(id)

    if category is None:
        return Response(content=f"No category with ID {id} found", status_code=404)
    else:
        return category