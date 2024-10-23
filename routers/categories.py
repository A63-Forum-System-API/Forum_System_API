from fastapi import APIRouter, Response, Depends, HTTPException
from pydantic import BaseModel
from schemas.category import Category
from services import category_service, user_service
from common.auth import get_current_user
from starlette import status
from common.custom_responses import ForbiddenAccess, NotFound, Locked, Unauthorized, OK, BadRequest, NoContent


categories_router = APIRouter(prefix="/categories", tags=['Categories'])


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


@categories_router.get("/{category_id}")
def get_category_by_id(category_id: int, current_user_id: int = Depends(get_current_user)):
    category = category_service.get_by_id(category_id)
    if category is None:
        return NotFound("Category")
    if category.is_private:
        if not category_service.validate_user_access(current_user_id, category_id):
            return ForbiddenAccess()

    return category_service.get_by_id_with_topics(category)
     


@categories_router.post("/", status_code=201)
def create_category(
    category: Category, current_user_id: int = Depends(get_current_user)
):
    if not user_service.is_admin(current_user_id):
        return ForbiddenAccess(content="Only admin can create categories")
    
    if category_service.title_exists(category.title):
        return BadRequest(content=f"Category with title '{category.title}' already exists")
    
    return category_service.create(category, current_user_id)
   


@categories_router.put("/{category_id}/access/{private_status_code}", status_code=204)
def change_category_private_status(
    category_id: int, private_status_code: int, current_user_id: int = Depends(get_current_user)
):
    if not user_service.is_admin(current_user_id):
        return ForbiddenAccess(content="Only admin can change category private status")
    
    if private_status_code not in (0, 1):
        return BadRequest(content="Private status code must be 0 or 1")
    
    category = category_service.get_by_id(category_id)
    if category is None:
        return NotFound("Category")
    
    if category.is_private == private_status_code:
        # Category with provided id and private status already has the given status. No change needed.
        return OK(content="This category already was set to the provided private status.")

    category_service.change_category_private_status(category_id, private_status_code)
    return OK("Category private status was successfully changed")
    


@categories_router.put("/{category_id}/locked-status/{locked_status_code}", status_code=204)
def change_category_lock_status(
    category_id: int, locked_status_code: int, current_user_id: int = Depends(get_current_user)
):
    if not user_service.is_admin(current_user_id):
        return ForbiddenAccess()
    
    if locked_status_code not in (0, 1):
        return BadRequest(content="Locked status code must be 0 or 1")
    
    category = category_service.get_by_id(category_id)
    if category is None:
        return NotFound("Category")
    
    if category.is_locked == locked_status_code:
        # Category with provided id and lock status already has the given status. No change needed.
        return OK(content="This category already was set to the provided lock status")

    
    category_service.change_category_lock_status(category_id, locked_status_code)
    return OK("Category lock status was successfully changed")
  


@categories_router.patch("/{category_id}/users/{user_id}/write-access/{write_access_code}", status_code=204)
def manage_user_access_to_private_category(
    category_id: int,
    user_id: int,
    write_access_code: int,
    current_user_id: int = Depends(get_current_user),
):
    if not user_service.is_admin(current_user_id):
        return ForbiddenAccess()
    if write_access_code not in (0, 1):
        return BadRequest(content="Access code must be 0 or 1")
    
    category = category_service.get_by_id(category_id)
    if category is None:
        return NotFound("Category")
    if not category.is_private:
        return BadRequest(content=f"Category ID: {category_id} is public")
    
    if not user_service.id_exists(user_id):
        return NotFound(content=f"User ID: {user_id}")
        
    category_service.manage_user_access_to_private_category(
        category_id, user_id, write_access_code)
    return OK("Access was successfully changed")


@categories_router.delete("/{category_id}/users/{user_id}/", status_code=204)
def remove_user_access_to_private_category(
    category_id: int,
    user_id: int,
    current_user_id: int = Depends(get_current_user),
):
    if not user_service.is_admin(current_user_id):
        return ForbiddenAccess(content="Only admin can remove user access to private category")
    
    category = category_service.get_by_id(category_id)
    if category is None:
        return NotFound("Category")
    if not category.is_private:
        return BadRequest(content=f"Category ID: {category_id} is public")
    
    if not user_service.id_exists(user_id):
        return NotFound(content=f"User ID: {user_id}")
        
    category_service.remove_user_access_to_private_category(category_id, user_id)
    return OK("Access was successfully deleted")
        


@categories_router.get("/{category_id}/private/users")
def get_privileged_users_by_category(
    category_id: int, current_user_id: int = Depends(get_current_user)
):
    if not user_service.is_admin(current_user_id):
        return ForbiddenAccess(content="Only admin can get privileged users by category")
    
    category = category_service.get_by_id(category_id)
    if category is None:
        return NotFound("Category")
    if not category.is_private:
        return BadRequest(content=f"Category ID: {category_id} is public")
    
    return category_service.get_privileged_users_by_category(category_id)

