from data.database import (
    insert_query,
    read_query,
    query_count,
    update_query,
    delete_query,
)
from schemas.category import Category, ViewAllCategories, SingleCategory
from schemas.category_accesses import Accesses
from schemas.topic import ViewAllTopics
from services import topic_service
from services.user_service import is_admin, id_exists as user_exists
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

    if is_admin(current_user_id):
        query += " WHERE is_private in (0, 1)"
    elif current_user_id is None:
        query += " WHERE is_private = 0"
    else:
        query += """ LEFT JOIN category_accesses ca
                    ON categories.id = ca.category_id
                    WHERE (is_private = 0 
                    OR (ca.user_id = ? 
                    AND ca.read_access = 1)) """
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


def get_by_id_with_topics(id: int, current_user_id: int):
    data = read_query(
        """SELECT id, title, description, is_private, is_locked, created_at, admin_id
            FROM categories
            WHERE id = ?""",
        (id,),
    )

    if not data:
        return None

    category = Category.from_query_result(*data[0])
    if category.is_private:
        # Check if the user has access
        # TODO think if we should validate this in router
        if not validate_user_access(current_user_id, category.id):
            raise Exception(
                f"User ID {current_user_id} is not authorized to access category ID {category.id}"
            )

    topics = get_category_topics(id)

    return SingleCategory(category=category, topics=topics)


def get_by_id(id: int) -> Category:
    """Get category id for internal use."""
    data = read_query(
        """SELECT id, title, description, is_private, is_locked, created_at, admin_id
            FROM categories
            WHERE id = ?""",
        (id,),
    )
    if not data:
        return None

    return Category.from_query_result(*data[0])


def get_category_topics(id: int) -> list[ViewAllTopics]: # TODO id -> category_id
    data = read_query(
        """SELECT id, title, is_locked, created_at, author_id
            FROM topics
            WHERE category_id = ?""",
        (id,),
    )
    topics = []
    for row in data:
        topic = ViewAllTopics(
            id=row[0],
            title=row[1],
            is_locked=row[2],
            created_at=row[3],
            author_id=row[4],
            category_id=id # TODO category_id
        )
        topics.append(topic)

    return topics


def exists(id: int) -> bool:
    return (
        query_count(
            """SELECT COUNT(*)
                       FROM categories 
                       WHERE id = ?""",
            (id,),
        )
        > 0
    )


def title_exists(title: str) -> bool:
    return (
        query_count(
            """SELECT COUNT(*) 
                       FROM categories 
                       WHERE title = ?""",
            (title,),
        )
        > 0
    )


def is_private(id: int) -> bool:
    result = read_query(
        """SELECT is_private FROM categories 
           WHERE id = ?""",
        (id,),
    )
    if not result:
        raise Exception(f"Category with ID: {id} not found")

    return result[0][0] == 1


def create(category: Category, current_user_id: int):
    if title_exists(category.title):
        raise Exception(f"Category with title: {category.title} already exists")

    query = """INSERT INTO categories (title, description, is_private, is_locked, admin_id)
                VALUES (?, ?, ?, ?, ?)"""

    generated_id = insert_query(
        query,
        (
            category.title,
            category.description,
            category.is_private,
            category.is_locked,
            current_user_id,
        ),
    )

    category = get_by_id(generated_id)
    if category.is_private:
        query = """INSERT INTO category_accesses 
                (user_id, category_id, write_access, read_access)
                VALUES (?, ?, ?, ?)"""
        insert_query(
            query,
            (
                current_user_id,
                category.id,
                1,
                1,
            ),
        )

    return category


def change_category_private_status(category_id: int, private_status_code: int):
    category = get_by_id(category_id)
    if not category:
        raise Exception(f"Category ID {category_id} not found")

    if category.is_private == private_status_code:
        # Category with provided id and private status already has the given status. No change needed.
        return

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
    deleted_rows = delete_query(query, (category_id, user_id))
    logger.info(f"{deleted_rows} row were deleted from category_accesses")


def change_category_lock_status(category_id: int, locked_status_code: int):
    category = get_by_id(category_id)
    if not category:
        raise Exception(f"Category ID {category_id} not found")

    if category.is_locked == locked_status_code:
        # Category with provided id and lock status already has the given status. No change needed.
        return

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
    if user_id is not None and not user_exists(user_id):
        raise Exception(f"User with ID {user_id} not found")

    if is_admin(user_id):
        return True
    if not is_private(category_id):
        return True
    if user_id is None:
        return False

    return (
        query_count(
            f"""SELECT COUNT(*)
                    FROM category_accesses 
                    WHERE category_id = ? 
                    AND user_id = ?
                    AND {access_type}_access = 1""",
            (category_id, user_id),
        )
        > 0
    )


# Service for category access
# def change_user_write_access_for_category(
#     category_id: int, user_id: int, write_access_code: int
# ):
#     if validate_user_access(user_id, category_id):
#         if write_access_code not in (0, 1):
#             raise Exception(f"Write access code must be 0 or 1")

#         data = read_query(
#             """SELECT user_id, category_id, write_access, read_access
#                                             FROM category_accesses
#                                             WHERE category_id = ?
#                                             AND user_id = ?""",
#             (category_id, user_id),
#         )
#         access_model_for_user = Accesses.from_query_result(*data[0])

#         if access_model_for_user.write_access == write_access_code:
#             raise Exception(
#                 f"User with ID {user_id} already has write access={write_access_code}"
#             )

#         query = """UPDATE category_accesses
#                 SET write_access = ?
#                 WHERE category_id = ?
#                 AND user_id = ?"""
#         update_query(query, (write_access_code, category_id, user_id))


# Service for category access
# def change_user_read_access_for_category(
#     category_id: int, user_id: int, read_access_code: int
# ):
#     if validate_user_access(user_id, category_id):
#         if read_access_code not in (0, 1):
#             raise Exception(f"Read access code must be 0 or 1")

#         data = read_query(
#             """SELECT user_id, category_id, write_access, read_access
#                 FROM category_accesses
#                 WHERE category_id = ?
#                 AND user_id = ?""",
#             (category_id, user_id),
#         )
#         access_model_for_user = Accesses.from_query_result(*data[0])

#         if access_model_for_user.read_access == read_access_code:
#             raise Exception(
#                 f"User with ID {user_id} already has read access={read_access_code}"
#             )

#         query = """UPDATE category_accesses
#                 SET read_access = ?
#                 WHERE category_id = ?
#                 AND user_id = ?"""
#         update_query(query, (read_access_code, category_id, user_id))


# Service for category access
def manage_user_access_to_private_category(
    category_id: int, user_id: int, code_read_access: int, code_write_access: int
):
    if not is_private(category_id):
        raise Exception(f"Category ID {category_id} is public")

    if not user_exists(user_id):
        raise Exception(f"User ID {user_id} not found")

    data = read_query(
        """SELECT user_id, category_id, write_access, read_access
                FROM category_accesses
                WHERE category_id = ?
                AND user_id = ?""",
        (category_id, user_id),
    )
    if data:
        access_model_for_user = Accesses.from_query_result(*data[0])
        if not code_read_access and not code_write_access:
            _remove_access_from_category_for_user(category_id, user_id)
            logger.info(
                f"Access for user ID {user_id} removed for category ID {category_id}"
            )
            return

        if (
            access_model_for_user.read_access == code_read_access
            and access_model_for_user.write_access == code_write_access
        ):
            logger.info(
                f"No access change for user ID {user_id} and category ID {category_id}"
            )
            return

        query = """UPDATE category_accesses 
                SET read_access = ?, write_access = ? 
                WHERE category_id = ?
                AND user_id = ?"""
        update_query(query, (code_read_access, code_write_access, category_id, user_id))
        logger.info(
            f"Access for user ID {user_id} and category ID {category_id} updated"
        )

        return
    else:
        if not code_read_access and not code_write_access:
            logger.info(
                f"User ID {user_id} already doesn't have access to category ID {category_id}"
            )
            return

        query = """INSERT INTO category_accesses 
                (user_id, category_id, read_access, write_access)
                VALUES (?, ?, ?, ?)"""

        insert_query(query, (user_id, category_id, code_read_access, code_write_access))
        logger.info(f"Access for user ID {user_id} and category ID {category_id} added")

        return



def get_privileged_users_by_category(category_id):
    if not is_private(category_id):
        raise Exception(f"Category ID {category_id} is public")

    data = read_query(
        """SELECT user_id, category_id, write_access, read_access
            FROM category_accesses
            WHERE category_id = ?""",
            (category_id,),
    )

    return [Accesses.from_query_result(*row) for row in data]
