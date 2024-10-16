from data.database import insert_query, read_query, query_count, update_query
from schemas.category import Category, ViewAllCategories
from schemas.topic import TopicView



def get_categories(
        search: str = None, 
        sort: str = None, 
        sort_by: str = None,
        limit: int = 10, 
        offset: int = 0
    ):
    query = "SELECT id, title, description, is_private, is_locked, created_at, admin_id FROM categories"
    params = []
    if search:
        query += " WHERE lower(title) LIKE ?"
        params.append(f"%{search.lower()}%")
    if sort:
        query += f" ORDER BY {sort_by} {sort}"

    query += " LIMIT ? OFFSET ?"
    params.extend((limit, offset))

    data = read_query(query, params)
        
    return [Category.from_query_result(*row) for row in data]


# def sort_categories(categories: list[ViewAllCategories], *, attribute='title', reverse=False):
#     if attribute == 'title':
#         def sort_fn(c: Category): return c.title
#     elif attribute == 'date':
#         def sort_fn(c: Category): return c.created_at

#     return sorted(categories, key=sort_fn, reverse=reverse)


def get_by_id(id: int):
    data = read_query(
        """SELECT id, title, description, is_private, is_locked, created_at, admin_id
            FROM categories
            WHERE id = ?""", (id,))
    
    if not data:
        return None
    
    category = Category.from_query_result(*data[0])
    category = category.model_dump()
    category["topics"] = get_category_topics(id)
    
    return category


def get_category_topics(id: int) -> list[TopicView]:
    data = read_query(
        """SELECT t.id, t.title, t.content, t.is_locked, t.created_at, t.author_id, br.reply_id
            FROM topics t
            LEFT JOIN best_replies br
            ON t.id = br.topic_id
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
            category_id=id
        )
        topics.append(topic)
    
    return topics


# def get_category_topics(id: int) -> list[Topic]:
#     data = read_query(
#         """SELECT id, title, content, is_locked, created_at, author_id, best_reply_id
#             FROM topics
#             WHERE category_id = ?""", (id,))
#     topics = []
#     for row in data:
#         topic = Topic(
#             id=row[0],
#             title=row[1],
#             content=row[2],
#             is_locked=row[3],
#             created_at=row[4],
#             author_id=row[5],
#             best_reply_id=row[6],
#             category_id=id
#         )
#         topics.append(topic)
    
#     return topics

def exists(id: int) -> bool:
    return any(
        read_query("""SELECT id, title 
                   FROM categories 
                   WHERE id = ?""", (id,)))


def name_exists(name: str) -> bool:
    return query_count("""SELECT COUNT(*) 
                       FROM categories 
                       WHERE name = ?""", (name,)) > 0


def create(category: Category, user_id: int):
    query = """INSERT INTO categories (title, description, author_id)
                VALUES (?, ?, ?)"""
    if name_exists(category.title):
        return Exception(f"Category with title: {category.title} already exists")
    
    generated_id = insert_query(query, (category.title, category.description, user_id))

    category.id = generated_id

    return category


def lock_category(category_id: int):
    if exists(category_id):
        query = """UPDATE categories 
                    SET is_locked = True 
                    WHERE id = ?"""
        update_query(query, (category_id,))
    else:
        raise Exception(f"Category ID {category_id} not found")


def unlock_category(category_id: int):
    if exists(category_id):
        query = """UPDATE categories 
                    SET is_locked = False 
                    WHERE id = ?"""
        update_query(query, (category_id,))
    else:
        raise Exception(f"Category ID {category_id} not found")


def make_private(category_id: int):
    if exists(category_id):
        query = """UPDATE categories 
                    SET is_private = True 
                    WHERE id = ?"""
        update_query(query, (category_id,))
    else:
        raise Exception(f"Category ID {category_id} not found")


def make_nonprivate(category_id: int):
    if exists(category_id):
        query = """UPDATE categories 
                    SET is_private = False 
                    WHERE id = ?"""
        update_query(query, (category_id,))
    else:
        raise Exception(f"Category ID {category_id} not found")