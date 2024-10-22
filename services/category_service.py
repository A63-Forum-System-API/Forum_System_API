from data.database import (
    insert_query,
    read_query,
    query_count,
    update_query,
    delete_query,
)
from schemas.category import Category, ViewAllCategories, SingleCategory
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

    query = """SELECT id, title, description, created_at 
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
    
    topics = get_category_topics(category.id)

    return SingleCategory(category=category, topics=topics)


def get_by_id(category_id: int) -> Category:
    data = read_query(
        """SELECT id, title, description, is_private, is_locked, created_at, admin_id
            FROM categories
            WHERE id = ?""",
        (category_id,),
    )
    if not data:
        return None

    return Category.from_query_result(*data[0])


def get_category_topics(category_id: int) -> list[ViewAllTopics]:
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
    result = read_query(
        """SELECT is_private FROM categories 
           WHERE id = ?""",
        (category_id,),
    )
    if not result:
        raise Exception(f"Category with ID: {category_id} not found")

    return result[0][0] == 1


def create(category: Category, current_user_id: int):
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
    query = """DELETE FROM category_accesses 
            WHERE category_id = ?"""
    deleted_rows = delete_query(query, (category_id,))
    logger.info(f"{deleted_rows} row(s) were deleted from category_accesses")


def _remove_access_from_category_for_user(category_id: int, user_id: int):
    query = """DELETE FROM category_accesses 
            WHERE category_id = ?
            AND user_id = ?"""
    deleted_row = delete_query(query, (category_id, user_id))
    logger.info(f"{deleted_row} row was deleted from category_accesses")


def change_category_lock_status(category_id: int, locked_status_code: int):
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
    
    query = """SELECT read_access
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
    category_id: int, user_id: int, access_code: int
):
    data = read_query(
        """SELECT user_id, category_id, read_access
                FROM category_accesses
                WHERE category_id = ?
                AND user_id = ?""",
        (category_id, user_id),
    )
    if data:
        access_model_for_user = Accesses.from_query_result(*data[0])

        if access_model_for_user.type_access == access_code:
            logger.info(
                f"No access change for user ID {user_id} and category ID {category_id}"
            )
            return

        query = """UPDATE category_accesses 
                SET read_access = ?
                WHERE category_id = ?
                AND user_id = ?"""
        update_query(query, (access_code,  category_id, user_id))
        logger.info(
            f"Access for user ID {user_id} and category ID {category_id} updated"
        )

        return
    else:
        query = """INSERT INTO category_accesses 
                (user_id, category_id, read_access)
                VALUES (?, ?, ?)"""

        insert_query(query, (user_id, category_id, access_code))
        logger.info(f"Access for user ID {user_id} and category ID {category_id} added")

        return


def remove_user_access_to_private_category(
    category_id: int, user_id: int,
):
    data = read_query(
        """SELECT user_id, category_id, read_access
                FROM category_accesses
                WHERE category_id = ?
                AND user_id = ?""",
        (category_id, user_id),
    )
    if data:
        _remove_access_from_category_for_user(category_id, user_id)

    

def get_privileged_users_by_category(category_id):
    data = read_query(
        """SELECT user_id, category_id, read_access
            FROM category_accesses
            WHERE category_id = ?""",
            (category_id,),
    )
    accesses = [Accesses.from_query_result(*row) for row in data]
    result = []
    for access in accesses:
        if access.type_access:
            access = access.model_dump()
            access["read_access"] = True
            access["write_access"] = True
            del access["type_access"]
            result.append(access)
        else:
            access = access.model_dump()
            access["read_access"] = True
            access["write_access"] = False
            del access["type_access"]
            result.append(access)
        
    return result


