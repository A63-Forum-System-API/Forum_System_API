from mariadb import connect
from mariadb.connections import Connection
import db_credentials


def _get_connection() -> Connection:
    return connect(
        user=db_credentials.username,
        password=db_credentials.password,
        host="localhost",
        port=3306,
        database="forum_system"
    )


def read_query(sql, sql_params=()):
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, sql_params)

        return list(cursor)


def insert_query(sql, sql_params=()):
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, sql_params)
        conn.commit()

        return cursor.lastrowid


def update_query(sql, sql_params=()):
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, sql_params)
        conn.commit()

        return True