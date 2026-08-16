import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_CONFIG = {
    "host": "127.0.0.1",
    "database": "monitoring",
    "user": "postgres",
    "password": "postgres",
    "port": 5432
}


def get_connection():
    return psycopg2.connect(
        cursor_factory=RealDictCursor,
        **DATABASE_CONFIG
    )



