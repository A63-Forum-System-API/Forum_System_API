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
    categories = category_service.get_categories(search, limit, offset)

    if sort and (sort == 'asc' or sort == 'desc'):
        return category_service.sort_categories(categories, reverse=sort == 'desc', attribute=sort_by)
    else:
        return categories


@categories_router.get('/{id}')
def get_category_by_id(id: int):
    category = category_service.get_by_id(id)

    if category is None:
        return Response(content=f"No category with ID {id} found", status_code=404)
    else:
        return category