from fastapi import APIRouter, Depends, Query, Path
from schemas.category import Category, CreateCategoryRequest
from services import category_service, user_service
from common.auth import get_current_user
from common.custom_responses import ForbiddenAccess, NotFound, OK, BadRequest, OnlyAdminAccess
from typing import Literal

categories_router = APIRouter(prefix="/categories", tags=["Categories"])


@categories_router.get("/")
def get_all_categories(
    search: str | None = Query(description="Search for categories by title", default=None),
    sort_by: Literal["title", "created_at"] | None = Query(description="Sort categories by title or created_at", default=None),
    sort: Literal["asc", "desc"] | None = Query(description="Sort categories asc or desc", default=None),
    limit: int = Query(description="Limit the number of categories returned", default=10, ge=1, le=100),
    offset: int = Query(description="Offset the number of categories returned", default=0, ge=0),
    current_user_id: int = Depends(get_current_user)
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
def get_category_by_id(category_id: int = Path(description="ID of the category to retrieve"), 
                       current_user_id: int = Depends(get_current_user)):
    category = category_service.get_by_id(category_id)
    if category is None:
        return NotFound("Category")
    if category.is_private:
        if not category_service.validate_user_access(current_user_id, category_id):
            return ForbiddenAccess()

    return category_service.get_by_id_with_topics(category)
     


@categories_router.post("/", status_code=201)
def create_category(
    category: CreateCategoryRequest, current_user_id: int = Depends(get_current_user)
):
    if not user_service.is_admin(current_user_id):
        return OnlyAdminAccess(content="create categories")
    
    if category_service.title_exists(category.title):
        return BadRequest(content=f"Category with title '{category.title}' already exists")
    
    return category_service.create(category, current_user_id)
   


@categories_router.put("/{category_id}/access/{access_type}", status_code=204)
def change_category_private_status(
    category_id: int = Path(description="ID of the category to manage access"), 
    access_type: Literal["public", "private"] = Path(description="Access type for category"),  
    current_user_id: int = Depends(get_current_user)
):
    if not user_service.is_admin(current_user_id):
        return OnlyAdminAccess(content="change category private status")
    
    private_status_code = 0 if access_type == "public" else 1
    
    # if private_status_code not in (0, 1):
    #     return BadRequest(content="Private status code must be 0 or 1")
    
    category = category_service.get_by_id(category_id)
    if category is None:
        return NotFound("Category ID: {category_id}")
    
    if category.is_private == private_status_code:
        # Category with provided id and private status already has the given status. No change needed.
        return OK(content=f"Category ID: {category_id} was already set to {access_type}.")

    category_service.change_category_private_status(category_id, private_status_code)
    return OK(f"Category ID: {category_id} private status was successfully changed")
    

@categories_router.put("/{category_id}/locked-status/{locked_status}", status_code=204)
def change_category_lock_status(
    category_id: int = Path(description="ID of the category to manage locked status"), 
    locked_status: Literal["lock", "unlock"] = Path(description="Locked status for category"), 
    current_user_id: int = Depends(get_current_user)
):
    if not user_service.is_admin(current_user_id):
        return OnlyAdminAccess("change locked status of a category")
    
    locked_status_code = 0 if locked_status == "unlock" else 1
    # if locked_status_code not in (0, 1):
    #     return BadRequest(content="Locked status code must be 0 or 1")
    
    category = category_service.get_by_id(category_id)
    if category is None:
        return NotFound(f"Category ID: {category_id}")
    
    if category.is_locked == locked_status_code:
        # Category with provided id and lock status already has the given status. No change needed.
        return OK(content=f"Category ID: {category_id} is already {locked_status}ed")

    
    category_service.change_category_lock_status(category_id, locked_status_code)
    return OK(f"Category ID: {category_id} locked status was successfully changed")
  


@categories_router.patch("/{category_id}/users/{user_id}/user-access/{user_access}", status_code=204)
def manage_user_access_to_private_category(
    category_id: int = Path(description="ID of the category"),
    user_id: int = Path(description="ID of the user"),
    user_access: Literal["read_only", "read_and_write"] = Path(description="User access type"),
    current_user_id: int = Depends(get_current_user),
):
    if not user_service.is_admin(current_user_id):
        return OnlyAdminAccess("manage user access to private category")
    
    write_access_code = 0 if user_access == "read_only" else 1
    # if write_access_code not in (0, 1):
    #     return BadRequest(content="Access code must be 0 or 1")
    
    category = category_service.get_by_id(category_id)
    if category is None:
        return NotFound("Category")
    if not category.is_private:
        return BadRequest(content=f"Category ID: {category_id} is public")
    
    if not user_service.id_exists(user_id):
        return NotFound(content=f"User ID: {user_id}")
        
    category_service.manage_user_access_to_private_category(
        category_id, user_id, write_access_code)
    return OK("User access was successfully changed")


@categories_router.delete("/{category_id}/users/{user_id}/", status_code=204)
def remove_user_access_to_private_category(
    category_id: int = Path(description="ID of the category"),
    user_id: int = Path(description="ID of the user"),
    current_user_id: int = Depends(get_current_user),
):
    if not user_service.is_admin(current_user_id):
        return OnlyAdminAccess(content="remove user access to private category")
    
    category = category_service.get_by_id(category_id)
    if category is None:
        return NotFound("Category")
    if not category.is_private:
        return BadRequest(content=f"Category ID: {category_id} is public")
    
    if not user_service.id_exists(user_id):
        return NotFound(content=f"User ID: {user_id}")
        
    message = category_service.remove_user_access_to_private_category(category_id, user_id)
    return OK(message)
        


@categories_router.get("/{category_id}/private/users")
def get_privileged_users_by_category(
    category_id: int, current_user_id: int = Depends(get_current_user)
):
    if not user_service.is_admin(current_user_id):
        return OnlyAdminAccess(content="get privileged users by category")
    
    category = category_service.get_by_id(category_id)
    if category is None:
        return NotFound("Category")
    if not category.is_private:
        return BadRequest(content=f"Category ID: {category_id} is public")
    
    return category_service.get_privileged_users_by_category(category_id)

