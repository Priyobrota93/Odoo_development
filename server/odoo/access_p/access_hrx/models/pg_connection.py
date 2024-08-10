import psycopg2
from psycopg2 import connect, Error as PsycopgError


def get_pg_access(env):
    pg_access = env["hr_mobile_access_input"].search([], order="id desc", limit=1)
    if not pg_access:
        print("No PostgreSQL access details found.")
        return None
    return pg_access


def get_pg_connection(pg_access):
    try:
        conn = connect(
            host=pg_access.pg_db_host,
            database=pg_access.pg_db_name,
            user=pg_access.pg_db_user,
            password=pg_access.pg_db_password,
        )
        return conn
    except PsycopgError as e:
        print(f"PostgreSQL connection error: {e}")
        return None

  