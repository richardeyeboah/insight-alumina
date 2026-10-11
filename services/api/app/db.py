import os
from contextlib import contextmanager

import psycopg
from psycopg.rows import dict_row


@contextmanager
def database():
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not configured")
    with psycopg.connect(url, row_factory=dict_row, connect_timeout=5) as connection:
        connection.execute("SET statement_timeout = '10s'")
        connection.execute("SET TIME ZONE 'UTC'")
        yield connection
