from fastapi import APIRouter
from starlette.templating import Jinja2Templates

categories_router = APIRouter(prefix='/categories')
templates = Jinja2Templates(directory='templates')


@categories_router.get("/")
def get_all_categories(
        search: str | None = Query(description="Search for categories by title", default=None),
        sort_by: Literal["title", "created_at"] | None = Query(description="Sort categories by title or created_at",
                                                               default=None),
        sort: Literal["asc", "desc"] | None = Query(description="Sort categories asc or desc", default=None),
        limit: int = Query(description="Limit the number of categories returned", default=10, ge=1, le=100),
        offset: int = Query(description="Offset the number of categories returned", default=0, ge=0),
        current_user_id: int = Depends(get_current_user)
):
    """
    View all categories based on optional search, sorting, and pagination parameters if the user
    has access to the categories. Params sort_by and sort must be included together or neither of them.

    Parameters:
        search (str | None): A string to filter categories by title. Defaults to None.
        sort_by (Literal["title", "created_at"] | None): The field to sort the categories by. Defaults to None.
        sort (Literal["asc", "desc"] | None): The direction of the sorting. Defaults to None.
        limit (int): The maximum number of categories to return. Defaults to 10.
        offset (int): The number of categories to skip before starting to collect the result
        set. Defaults to 0.
        current_user_id (int): The ID of the current user, provided by the authentication
        dependency.

    Returns:
        Response: List of categories based on the provided parameters or BadRequest error messages
        for invalid inputs.
    """

    # validation
    if not sort in (None, "asc", "desc"):
        return BadRequest(
            content=f"Invalid value for sort: {sort}. Valid values are: asc, desc"
        )

    if sort and sort_by not in ("title", "created_at"):
        return BadRequest(
            content=f"Invalid value for sort_by: {sort_by}. Valid values are: title, created_at"
        )

    if limit < 1 or limit > 100:  # fastapi checks if limit is int
        return BadRequest(
            content=f"Invalid value for limit: {limit}. Valid values are: int [1-100]"
        )

    if offset < 0:
        return BadRequest(
            content=f"Invalid value for offset: {offset}. Valid values are: int >= 0"
        )

    return category_service.get_categories(
        search, sort, sort_by, limit, offset, current_user_id
    )
