from data.database import (
    insert_query,
    read_query,
    query_count,
    update_query,
    delete_query,
)
from schemas.category import Category, ViewAllCategories, SingleCategory, CreateCategoryRequest
from schemas.category_accesses import Accesses
from schemas.topic import ViewAllTopics, ListOfTopics
from services import topic_service
from services import user_service
import logging

logger = logging.getLogger(__name__)
logger.propagate = True


def get_categories(
    search: str = None,
    sort: str = None,
    sort_by: str = None,
    limit: int = 10,
    offset: int = 0,
    current_user_id: int = None,
):
    """
    Retrieve from the database a list of categories with optional filtering and sorting.
    The visibility of categories is determined based on the user's access level. 
    Admin users can see all categories, while non-admin users can only view public categories 
    or categories they have access to.

    Parameters:
        search (str, optional): A string to filter categories by title. Defaults to None.
        sort (str, optional): Specifies the sorting order, either 'asc' or 'desc'. Defaults to None, meaning no sorting is applied.
        sort_by (str, optional): Specifies the field by which to sort the results, possible values are: 'title' or 'created_at'. Defaults to None, meaning no sorting is 
        applied.
        limit (int, optional): The maximum number of categories to return. Defaults to 10, with a minimum value of 1 and a maximum of 100.
        offset (int, optional): The number of categories to skip before returning results. Defaults to 0.
        current_user_id (int, optional): The ID of the currently authenticated user. Defaults to None, indicating an unauthenticated user.

    Returns:
        lst: A list of `ViewAllCategories` instances, each representing a category that matches the query criteria.
    """

    query = """SELECT id, title, description, is_private, is_locked, created_at 
               FROM categories
               """
    params = []

    if user_service.is_admin(current_user_id):
        query += " WHERE is_private in (0, 1)"
    elif current_user_id is None:
        query += " WHERE is_private = 0"
    else:
        query += """ LEFT JOIN category_accesses ca
                    ON categories.id = ca.category_id
                    WHERE (is_private = 0 
                    OR (ca.user_id = ?))"""
        params.append(current_user_id)

    if search:
        query += " AND lower(title) LIKE ?"
        params.append(f"%{search.lower()}%")
    if sort:
        query += f" ORDER BY {sort_by} {sort}"

    query += " LIMIT ? OFFSET ?"
    params.extend((limit, offset))
    logger.info(query)
    logger.info(params)

    data = read_query(query, params)

    return [ViewAllCategories.from_query_result(*row) for row in data]


def get_by_id_with_topics(category: Category):
    """
    Retrieve a category along with its associated topics.
    Takes a `Category` object as input and fetches all topics related to that category. 
    
    Parameters:
        category (Category): An instance of the `Category` class.

    Returns:
        SingleCategory: An instance of `SingleCategory` containing the category details
        and a list of its associated topics.
    """
    
    topics = get_category_topics(category.id)

    return SingleCategory(category=category, topics=topics)


def get_by_id(category_id: int) -> Category:
    data = read_query(
        """SELECT id, title, description, is_private, is_locked, created_at, admin_id
            FROM categories
            WHERE id = ?""",
        (category_id,),
    )
    """
    Retrieve from the databasa a category by its ID.

    Parameters:
        category_id (int): The ID of the category to retrieve.

    Returns:
        Category: An instance of the `Category` class or None.
    """

    if not data:
        return None

    return Category.from_query_result(*data[0])


def get_category_topics(category_id: int) -> list[ListOfTopics]:
    """
    Retrieve from the database a list of topics associated with a specific category.

    Parameters:
        category_id (int): The ID of the category for which to retrieve topics.

    Returns:
        lst: A list of `ListOfTopics` instances representing the topics associated with 
        the specified category or an empty list if no topics are found.
    """
        
    data = read_query(
        """SELECT id, title, is_locked, created_at, author_id
            FROM topics
            WHERE category_id = ?""",
        (category_id,),
    )
    topics = []
    for row in data:
        topic = ListOfTopics(
            id=row[0],
            title=row[1],
            is_locked=row[2],
            created_at=row[3],
            author_id=row[4],
            category_id=category_id 
        )
        topics.append(topic)

    return topics


def exists(category_id: int) -> bool:
    """
    Check if a category exists in the database by its ID.

    Parameters:
        category_id (int): The ID of the category to check for existence.

    Returns:
        bool: True if the category exists or False if not found.
    """

    return (
        query_count(
            """SELECT COUNT(*)
                       FROM categories 
                       WHERE id = ?""",
            (category_id,),
        )
        > 0
    )


def title_exists(category_title: str) -> bool:
    """
    Check if a category with the specified title exists in the database.

    Parameters:
        category_title (str): The title of the category to check for existence.

    Returns:
        bool: True if a category with the specified title exists or False otherwise.
    """

    return (
        query_count(
            """SELECT COUNT(*) 
                       FROM categories 
                       WHERE title = ?""",
            (category_title,),
        )
        > 0
    )


def is_private(category_id: int) -> bool:
    """
    Check in the database if a category is private based on its ID.

    Parameters:
        category_id (int): The ID of the category to check for privacy status.

    Returns:
        bool: True if the category is private or False otherwise. Raises an exception if no category 
        is found with that ID.
    """

    result = read_query(
        """SELECT is_private FROM categories 
           WHERE id = ?""",
        (category_id,),
    )
    if not result:
        raise Exception(f"Category with ID: {category_id} not found")

    return result[0][0] == 1


def create(category: CreateCategoryRequest, current_user_id: int):
    """
    Create a new category in the database, using the provided CreateCategoryRequest object 
    and the current user ID.

    Parameters:
        category (CreateCategoryRequest): An instance of the `CreateCategoryRequest` class.
        current_user_id (int): The ID of the user creating the category.

    Returns:
        Category: An instance of the `Category` class with all attributes of the newly created category.
    """
        
    query = """INSERT INTO categories (title, description, is_private, admin_id)
                VALUES (?, ?, ?, ? )"""

    generated_id = insert_query(
        query,
        (
            category.title,
            category.description,
            category.is_private,
            current_user_id,
        ),
    )

    category = get_by_id(generated_id)

    return category


def change_category_private_status(category_id: int, private_status_code: int):
    """
    Change the privacy status of a category in the database.
    If the category is changed from private to public, all user access associated with that category
    will be removed, because public categories are accessible to everyone.

    Parameters:
        category_id (int): The ID of the category whose privacy status is to be modified.
        private_status_code (int): The privacy status code (0 for public and 1 for private).

    Returns:
        None: The function does not return a value. It performs an update on the database and may modify user access.
    """
  
    query = """UPDATE categories 
            SET is_private = ? 
            WHERE id = ?"""
    update_query(query, (private_status_code, category_id))
    if private_status_code == 0:
        # The category was initialy private and now it is changed to public.
        # Remove all user access to this category from category_accesses.
        # Public categories are accessible to anyone.
        # In case the category is changed back to private, no previous user access will exist.
        _remove_access_from_category(category_id)
  

def _remove_access_from_category(category_id: int):
    """
    Remove from the database all user access associated with a specific category ID.

    Parameters:
        category_id (int): The ID of the category for which all user access should be removed.

    Returns:
        None: This function does not return a value. It performs a deletion operation on the database.
    """
        
    query = """DELETE FROM category_accesses 
            WHERE category_id = ?"""
    deleted_rows = delete_query(query, (category_id,))
    logger.info(f"{deleted_rows} row(s) were deleted from category_accesses")


def _remove_access_from_category_for_user(category_id: int, user_id: int):
    """
    Remove from the database a user access entry for the specified user and category.

    Parameters:
        category_id (int): The ID of the category from which to remove user access.
        user_id (int): The ID of the user to be revoked.

    Returns:
        None: This function does not return a value. It performs a deletion operation on the database.
    """

    query = """DELETE FROM category_accesses 
            WHERE category_id = ?
            AND user_id = ?"""
    deleted_row = delete_query(query, (category_id, user_id))
    logger.info(f"{deleted_row} row was deleted from category_accesses")


def change_category_lock_status(category_id: int, locked_status_code: int):
    """
    Update the locked status of a specific category in the database.

    Parameters:
        category_id (int): The ID of the category whose locked status is to be updated.
        locked_status_code (int): The locked status code (1 to lock and 0 to unlock).

    Returns:
        None: This function does not return a value. It performs an update operation on the database.
    """

    query = """UPDATE categories 
            SET is_locked = ? 
            WHERE id = ?"""
    update_query(query, (locked_status_code, category_id))


# Service for category access
def validate_user_access(user_id: int, category_id: int, access_type: str = "read"):
    """
    Validates if a user has access to a category.
    Admin has access to all categories.
    Params:
        user_id: int
        category_id: int
        access_type: str ["read", "write"] - access type to be validated

    Returns True if has access and False if not.
    Raises exception if user or category id doesn't exist.
    """

    if access_type not in ("read", "write"):
        raise Exception(f"Invalid access type: {access_type}")

    if not exists(category_id):
        raise Exception(f"Category with ID {category_id} not found")

    if user_service.is_admin(user_id):
        return True
    if not is_private(category_id):
        return True
    if user_id is None:
        return False
    
    query = """SELECT write_access
            FROM category_accesses 
            WHERE category_id = ? 
            AND user_id = ?"""

    access = read_query(query, (category_id, user_id))
    
    if not access:
        return False
    if access_type == "read":
        return True
    else:
        return bool(access[0][0])


# Service for category access
def manage_user_access_to_private_category(
    category_id: int, user_id: int, write_access_code: int
):
    """
    Manage a user's access level for a specific private category. 
    If the access record exists but the write access level differs from the given `write_access_code`, 
    it updates the user's access level. If no access record exists, it creates a new record 
    with the specified access level.

    Parameters:
        category_id (int): The ID of the private category to manage access for.
        user_id (int): The ID of the user whose access level is being managed.
        write_access_code (int): The access level code (1 for read-and-write access and 0 for read-only).

    Returns:
        None: This function does not return a value. It either updates or inserts a record in the database.
    """
        
    data = read_query(
        """SELECT user_id, category_id, write_access
                FROM category_accesses
                WHERE category_id = ?
                AND user_id = ?""",
        (category_id, user_id),
    )
    if data:
        access_model_for_user = Accesses.from_query_result(*data[0])

        if access_model_for_user.write_access == write_access_code:
            logger.info(
                f"No access change for user ID {user_id} and category ID {category_id}"
            )
            return

        query = """UPDATE category_accesses 
                SET write_access = ?
                WHERE category_id = ?
                AND user_id = ?"""
        update_query(query, (write_access_code,  category_id, user_id))
        logger.info(
            f"Access for user ID {user_id} and category ID {category_id} updated"
        )

        return
    else:
        query = """INSERT INTO category_accesses 
                (user_id, category_id, write_access)
                VALUES (?, ?, ?)"""

        insert_query(query, (user_id, category_id, write_access_code))
        logger.info(f"Access for user ID {user_id} and category ID {category_id} added")

        return


def remove_user_access_to_private_category(
    category_id: int, user_id: int,
) -> str:
    """
    Remove a user's access to a specific private category.

    Parameters:
        category_id (int): The ID of the private category to remove access from.
        user_id (int): The ID of the user whose access is being removed.

    Returns:
        str: A message indicating the result of the operation.
    """

    data = read_query(
        """SELECT user_id, category_id, write_access
                FROM category_accesses
                WHERE category_id = ?
                AND user_id = ?""",
        (category_id, user_id),
    )
    if data:
        _remove_access_from_category_for_user(category_id, user_id)
        message = "Access was successfully deleted"
    else:
        message = "User has no access to the category"
    
    return message

    

def get_privileged_users_by_category(category_id):
    """
    Retrieve from the database a list of all users with their access details 
    to a specified private category.

    Parameters:
        category_id (int): The ID of the category to retrieve privileged users for.

    Returns:
        list[dict]: A list of dictionaries, each representing a user's access permissions 
        for the specified category.
    """

    data = read_query(
        """SELECT ca.user_id, u.username, ca.category_id, ca.write_access
            FROM category_accesses ca
            LEFT JOIN users u 
            ON ca.user_id = u.id
            WHERE ca.category_id = ?""",
            (category_id,),
    )
    accesses = [Accesses.from_query_result(*row) for row in data]
    result = []
    for access in accesses:
        if access.write_access:
            access = access.model_dump()
            access["read_access"] = True
            result.append(access)
        else:
            access = access.model_dump()
            access["read_access"] = True
            access["write_access"] = False
            result.append(access)
        
    return result


