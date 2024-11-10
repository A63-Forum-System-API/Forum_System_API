from fastapi import APIRouter, Request, Query, Depends, Form, HTTPException, status
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates
from common.auth import get_current_user
from schemas.category import CreateCategoryRequest
from services import category_service
from services import user_service
from common.custom_responses import ForbiddenAccess, NotFound, OK, BadRequest, OnlyAdminAccess
import logging

categories_router = APIRouter(prefix='/categories')
templates = Jinja2Templates(directory='templates')
logger = logging.getLogger(__name__)

@categories_router.get("/")
def get_categories(
        request: Request,
        search: str = Query(default=""),
        error: str | None = None,
):
    error_messages = {
        "not_authorized": "You need to login first!",
        "invalid_token": "Your sesh has expired! Please login again!",
        "unknown_error": "Oops! Something went wrong while loading categories 🙈",
        "not_found": "Category not found",
    }
    is_admin = False
    try:
        token = request.cookies.get("token")
        # flash_message = request.cookies.get("flash_message")

        if not token:
            return RedirectResponse(
                url="/?error=not_authorized",
                status_code=302
            )

        try:
            current_user_id = get_current_user(token)
            is_admin = user_service.is_admin(current_user_id)

        except:
            return RedirectResponse(
                url="/?error=invalid_token",
                status_code=302
            )


        categories = category_service.get_categories(
            search=search,
            sort="asc",
            sort_by="title",
            limit=100,
            offset=0,
            current_user_id=current_user_id
        )

        response = templates.TemplateResponse(
            request=request, name='categories.html',
            context={
                "categories": categories,
                "search": search,
                "is_admin": is_admin,
                "error": error_messages.get(error),
                # "flash_message": flash_message,
            }
        )
        # response.delete_cookie("flash_message")
        return response

    except Exception as e:
        return templates.TemplateResponse(
            request=request, name="categories.html",
            context={
                "categories": [],
                "search": search,
                "is_admin": is_admin,
                "error": error_messages.get(error or "unknown_error"),
            }
        )


@categories_router.post("/toggle-lock")
def toggle_lock(
    request: Request,
    category_id: int = Form(...),
    locked_status: str = Form(...),
):
    try:
        referer_url = request.headers.get("referer", "/categories/")
        token = request.cookies.get("token")
        if not token:
            return RedirectResponse(
                url="/?error=not_authorized",
                status_code=302
            )

        try:
            current_user_id = get_current_user(token)

        except:
            return RedirectResponse(
                url="/?error=invalid_token",
                status_code=302
            )
        
        is_admin = user_service.is_admin(current_user_id)
        if not is_admin:
            return RedirectResponse(
                url="/categories/?error=not_authorized",
                status_code=302
            )
    
        locked_status_code = 0 if locked_status == "unlock" else 1
        
        category = category_service.get_by_id(category_id)
        if category is None:
            return RedirectResponse(
                url="/categories/?error=not_found",
                status_code=302
            )
        
        if category.is_locked == locked_status_code:
            # Category with provided id and lock status already has the given status. No change needed.
            return RedirectResponse(
                url=referer_url,
                status_code=303,
            )

        
        category_service.change_category_lock_status(category_id, locked_status_code)
        response = RedirectResponse(
                url=referer_url,
                status_code=303,
            )
        # response.set_cookie(key="flash_message", value=f"Category id {category_id} was successfully updated!")
        return response
        

    except Exception as e:
        return RedirectResponse(
                url="/categories/?error=unknown_error",
                status_code=302
            )


@categories_router.post("/toggle-access")
def toggle_access(
    request: Request,
    category_id: int = Form(...),
    access_type: str = Form(...),
):
    try:
        referer_url = request.headers.get("referer", "/categories/")
        token = request.cookies.get("token")
        if not token:
            return RedirectResponse(
                url="/?error=not_authorized",
                status_code=302
            )

        try:
            current_user_id = get_current_user(token)

        except:
            return RedirectResponse(
                url="/?error=invalid_token",
                status_code=302
            )
        
        is_admin = user_service.is_admin(current_user_id)
        if not is_admin:
            return RedirectResponse(
                url="/categories/?error=not_authorized",
                status_code=302
            )
    
        access_type = 0 if access_type == "public" else 1
        
        category = category_service.get_by_id(category_id)
        if category is None:
            return RedirectResponse(
                url="/categories/?error=not_found",
                status_code=302
            )
        
        if category.is_private == access_type:
            # Category with provided id and access_type already has the given status. No change needed.
            return RedirectResponse(
                url=referer_url,
                status_code=303,
            )

        
        category_service.change_category_private_status(category_id, access_type)
        response = RedirectResponse(
                url=referer_url,
                status_code=303,
            )
        # response.set_cookie(key="flash_message", value=f"Category id {category_id} was successfully updated!")
        return response
        

    except Exception as e:
        return RedirectResponse(
                url="/categories/?error=unknown_error",
                status_code=302
            )



@categories_router.post('/')
def create_new_category(
        request: Request,
        title: str = Form(...),
        description: str = Form(...)):

    try:
        token = request.cookies.get("token")
        if not token:
            return RedirectResponse(
                url="/?error=not_authorized",
                status_code=302
            )

        current_user_id = get_current_user(token)

        if category_service.title_exists(title):
            return templates.TemplateResponse(
                request=request, name="categories.html",
                context={
                    "error": f"Category with title '{title}' already exists! 🙈"
                }
            )

        category = CreateCategoryRequest(title=title, description=description)
        category_service.create(category, current_user_id)

        return RedirectResponse(
            url=f"/categories",
            status_code=302
        )

    except Exception as e:
        error_message = str(e)
        if "title" in str(e):
            error_message = "Title should have at least 5 characters"
        elif "description" in str(e):
            error_message = "Description must be at least 5 characters"

        return templates.TemplateResponse(
            name="categories.html",
            context={
                "request": request,
                "error": f"{error_message} 🙈",
            },
        )


@categories_router.get("/{category_id}/manage-access")
def manage_access(request: Request, category_id: int, error: str | None = None,):

    error_messages = {
        "not_authorized": "You are not authorized!",
        "unknown_error": "Oops! Something went wrong while loading categories 🙈",
        "not_found": "Category not found",
    }

    try:
        referer_url = request.headers.get("referer", "/categories/")
        # flash_message = request.cookies.get("flash_message")
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
        
        is_admin = user_service.is_admin(current_user_id)
        if not is_admin:
            return RedirectResponse(
                url="/categories/?error=not_authorized",
                status_code=302
            )
        
        category = category_service.get_by_id(category_id)
        if category is None:
            return RedirectResponse(
                url="/categories/?error=not_found",
                status_code=302
            )
        if not category.is_private:
            return RedirectResponse(
                url="/categories/?error=unknown_error",
                status_code=302
            )
        
        accesses = category_service.get_privileged_users_by_category(category_id)

        response = templates.TemplateResponse(
            request=request, name='access_category.html',
            context={
                "category": category,
                "accesses": accesses,
                "error": error_messages.get(error),
                # "flash_message": flash_message,
            }
        )
        # response.delete_cookie("flash_message")
        return response
        
    except Exception as e:
        logger.exception(e)
        return RedirectResponse(
                url="/categories/?error=unknown_error",
                status_code=302
            )


@categories_router.post("/remove-access")
def remove_access(
    request: Request,
    category_id: int = Form(...),
    user_id: int = Form(...),
):
    try:
        referer_url = request.headers.get("referer", "/categories/")
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
        
        is_admin = user_service.is_admin(current_user_id)
        if not is_admin:
            return RedirectResponse(
                url="/categories/?error=not_authorized",
                status_code=302
            )
             
        if not category_service.exists(category_id):
            return RedirectResponse(
                url="/categories/?error=not_found",
                status_code=302
            )
        
        if not user_service.id_exists(user_id):
            return RedirectResponse(
                url="/categories/?error=unknown_error",
                status_code=302
            )
    
        category_service.remove_user_access_to_private_category(category_id, user_id)
        response = RedirectResponse(
                url=referer_url,
                status_code=303,
            )
        # response.set_cookie(key="flash_message", value=f"User id {user_id} was successfully removed!")
        return response
        

    except Exception as e:
        return RedirectResponse(
                url="/categories/?error=unknown_error",
                status_code=302
            )

@categories_router.post("/change-user-access")
def change_user_access(
    request: Request,
    category_id: int = Form(...),
    user_id: int = Form(...),
    access_type: str = Form(...),
):
    try:
        referer_url = request.headers.get("referer", "/categories/")
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
        
        is_admin = user_service.is_admin(current_user_id)
        if not is_admin:
            return RedirectResponse(
                url="/categories/?error=not_authorized",
                status_code=302
            )
        
        category = category_service.get_by_id(category_id)
        if category is None:
            return RedirectResponse(
                url="/categories/?error=not_found",
                status_code=302
            )
        if not category.is_private:
            return RedirectResponse(
                url="/categories/?error=unknown_error",
                status_code=302
            )
        
        if not user_service.id_exists(user_id):
            return RedirectResponse(
                url="/categories/?error=unknown_error",
                status_code=302
            )
        
        access_type = 1 if access_type == "read_and_write" else 0
    
        category_service.manage_user_access_to_private_category(category_id, user_id, access_type)
        response = RedirectResponse(
                url=referer_url,
                status_code=303,
            )
        # response.set_cookie(key="flash_message", value=f"User id {user_id} was successfully updated")
        return response 

    except Exception as e:
        logger.exception(e)
        return RedirectResponse(
                url="/categories/?error=unknown_error",
                status_code=302
            )


@categories_router.post("/add-user-access")
def change_user_access(
    request: Request,
    category_id: int = Form(...),
    username: str = Form(...),
    access_type: str = Form(...),
):
    try:
        referer_url = request.headers.get("referer", "/categories/")
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
        
        is_admin = user_service.is_admin(current_user_id)
        if not is_admin:
            return RedirectResponse(
                url="/categories/?error=not_authorized",
                status_code=302
            )
        
        category = category_service.get_by_id(category_id)
        if category is None:
            return RedirectResponse(
                url="/categories/?error=not_found",
                status_code=302
            )
        if not category.is_private:
            return RedirectResponse(
                url="/categories/?error=unknown_error",
                status_code=302
            )
        
        user = user_service.get_user_by_username(username)
        
        if not user:
            return RedirectResponse(
                url="/categories/?error=unknown_error",
                status_code=302
            )
        
        user_id: int = user["id"]
        if category_service.has_access(category_id, user_id):
            response = RedirectResponse(
                url=referer_url,
                status_code=303,
            )
            # response.set_cookie(key="flash_message", value=f"User id {user_id} already is added to the category")
            return response 

        
        access_type = 1 if access_type == "read_and_write" else 0
    
        category_service.manage_user_access_to_private_category(category_id, user_id, access_type)
        response = RedirectResponse(
                url=referer_url,
                status_code=303,
            )
        # response.set_cookie(key="flash_message", value=f"User id {user_id} was successfully added")
        return response 

    except Exception as e:
        logger.exception(e)
        return RedirectResponse(
                url="/categories/?error=unknown_error",
                status_code=302
            )
