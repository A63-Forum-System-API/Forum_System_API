from data.database import insert_query, read_query, query_count, update_query
from schemas.category import Category, ViewAllCategories
from schemas.category_accesses import Accesses
from schemas.topic import TopicView
from services.user_service import id_exists as user_exists

class UnauthorizedException(Exception):
    pass


def get_categories(
        search: str = None, 
        sort: str = None, 
        sort_by: str = None,
        limit: int = 10, 
        offset: int = 0,
        private: int=0,
        locked: int=0,
    ):
    
    query = "SELECT id, title, description, is_private, is_locked, created_at, admin_id FROM categories"
    params = []
    if private:
        data = read_query("""SELECT id, title, description, is_private, is_locked, created_at, admin_id 
                          FROM categories
                          WHERE is_private = ? """, (private,))

        return [Category.from_query_result(*row) for row in data]
    
    if locked:
        data = read_query("""SELECT id, title, description, is_private, is_locked, created_at, admin_id 
                          FROM categories
                          WHERE is_locked = ? """, (locked,))

        return [Category.from_query_result(*row) for row in data]


    if search:
        query += " WHERE lower(title) LIKE ?"
        params.append(f"%{search.lower()}%")
    if sort:
        query += f" ORDER BY {sort_by} {sort}"

    query += " LIMIT ? OFFSET ?"
    params.extend((limit, offset))

    data = read_query(query, params)
        
    return [Category.from_query_result(*row) for row in data]



def get_by_id(id: int, current_user_id: int):
    data = read_query(
        """SELECT id, title, description, is_private, is_locked, created_at, admin_id
            FROM categories
            WHERE id = ?""", (id,))
    
    if not data:
        return None
    
    category = Category.from_query_result(*data[0])
    if category.is_private:
        # Check if the user has access
        if not validate_user_access(current_user_id, category.id):
            raise Exception(
                f"User ID {current_user_id} is not authorized to access category ID {category.id}")
    category = category.model_dump()
    category["topics"] = get_category_topics(id)
    
    return category


def get_category_topics(id: int) -> list[TopicView]:
    data = read_query(
        """SELECT id, title, content, is_locked, created_at, author_id, best_reply_id
            FROM topics
            WHERE category_id = ?""", (id,))
    topics = []
    for row in data:
        topic = TopicView(
            id=row[0],
            title=row[1],
            content=row[2],
            is_locked=row[3],
            created_at=row[4],
            author_id=row[5],
            best_reply_id=row[6],
            category_id=id,
            all_replies=[],
        )
        topics.append(topic)
    
    return topics


def exists(id: int) -> bool:
    return query_count("""SELECT COUNT(*)
                       FROM categories 
                       WHERE id = ?""", (id,)) > 0


def title_exists(title: str) -> bool:
    return query_count("""SELECT COUNT(*) 
                       FROM categories 
                       WHERE title = ?""", (title,)) > 0

def is_private(id: int) -> bool:
    return query_count("""SELECT COUNT(*) 
                       FROM category_accesses 
                       WHERE category_id = ?""", (id,)) > 0


def create(category: Category, current_user_id: int):
    if title_exists(category.title):
        raise Exception(f"Category with title: {category.title} already exists")
    
    query = """INSERT INTO categories (title, description, is_private, is_locked, admin_id)
                VALUES (?, ?, ?, ?, ?)"""
    
    generated_id = insert_query(query, (category.title, 
                                        category.description, 
                                        category.is_private, 
                                        category.is_locked, 
                                        current_user_id))

    category.id = generated_id
    if category.is_private:
        query = """INSERT INTO category_accesses (user_id, category_id, write_access, read_access)
                VALUES (?, ?, ?, ?)"""
        insert_query(query, (current_user_id, 
                             category.id, 
                             1, 1,))

    return category



def change_category_private_status(category_id: int, private_status_code: int):
    category = get_by_id(category_id)
    if not category:
        raise Exception(f"Category ID {category_id} not found")
    if private_status_code not in (0, 1):
        raise Exception(f"Private status code must be 0 or 1")
    if category.is_private == private_status_code:
        raise Exception(f"Category with ID {category_id} already has private status={private_status_code}")
    
    query = """UPDATE categories 
            SET is_private = ? 
            WHERE id = ?"""
    update_query(query, (private_status_code, category_id))



def change_category_lock_status(category_id: int, locked_status_code: int):
    category = get_by_id(category_id)
    if not category:
        raise Exception(f"Category ID {category_id} not found")
    if locked_status_code not in (0, 1):
        raise Exception(f"Locked status code must be 0 or 1")
    if category.is_locked == locked_status_code:
        raise Exception(f"Category with ID {category_id} already has locked status={locked_status_code}")
    
    query = """UPDATE categories 
            SET is_locked = ? 
            WHERE id = ?"""
    update_query(query, (locked_status_code, category_id))


# Service for category access
def validate_user_access(user_id: int, category_id: int, access_type: str = "read"): 
    """
    Validates if a user has access to a category.
    Params: 
        user_id: int
        category_id: int
        access_type: str ["read", "write"] - access type to be validated

    Returns True if has access and False if not.
    Raises exception if user or category id doesn't exist.
    """
    if access_type not in ("read", "write"):
        raise Exception(f"Invalid access type: {access_type}")

    if exists(category_id) and user_exists(user_id):
        if query_count("""SELECT COUNT(*) FROM categories WHERE id = ? AND is_private = 1""", (category_id,)) == 0:
            return True
        
        return query_count(f"""SELECT COUNT(*)
                       FROM category_accesses 
                       WHERE category_id = ? 
                       AND user_id = ?
                       AND {access_type}_access = 1""", (category_id, user_id)) > 0
    else:
        raise Exception(f"Category with ID {category_id} or user with ID {user_id} not found")


# Service for category access
def change_user_write_access_for_category(category_id: int, user_id: int, write_access_code: int):
    if validate_user_access(user_id, category_id):
        if write_access_code not in (0, 1):
            raise Exception(f"Write access code must be 0 or 1")
        
        data = read_query("""SELECT user_id, category_id, write_access, read_access
                                            FROM category_accesses
                                            WHERE category_id = ?
                                            AND user_id = ?""", (category_id, user_id))
        access_model_for_user = Accesses.from_query_result(*data[0])
        
        
        if access_model_for_user.write_access == write_access_code:
            raise Exception(f"User with ID {user_id} already has write access={write_access_code}")
    
        query = """UPDATE category_accesses 
                SET write_access = ? 
                WHERE category_id = ?
                AND user_id = ?"""
        update_query(query, (write_access_code, category_id, user_id))


# Service for category access
def change_user_read_access_for_category(category_id: int, user_id: int, read_access_code: int):
    if validate_user_access(user_id, category_id):
        if read_access_code not in (0, 1):
            raise Exception(f"Read access code must be 0 or 1")
        
        data = read_query("""SELECT user_id, category_id, write_access, read_access
                                            FROM category_accesses
                                            WHERE category_id = ?
                                            AND user_id = ?""", (category_id, user_id))
        access_model_for_user = Accesses.from_query_result(*data[0])
        
        
        if access_model_for_user.read_access == read_access_code:
            raise Exception(f"User with ID {user_id} already has read access={read_access_code}")
    
        query = """UPDATE category_accesses 
                SET read_access = ? 
                WHERE category_id = ?
                AND user_id = ?"""
        update_query(query, (read_access_code, category_id, user_id))


def add_user_to_private_category(category_id: int, user_id: int, code_read_access: int, code_write_access: int):
    if is_private(category_id) and user_exists(user_id):
        if code_read_access not in (0, 1) or code_write_access not in (0, 1):
            raise Exception(f"Write and read access code must be 0 or 1")
      
        query = """INSERT INTO category_accesses (user_id, category_id, code_read_access, code_write_access)
                VALUES (?, ?, ?, ?)"""

        insert_query(query, (user_id, category_id, code_read_access, code_write_access))
                                       
   
