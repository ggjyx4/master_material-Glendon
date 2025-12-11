import os
import psycopg2
from psycopg2.extras import RealDictCursor

class BaseRepository:
    def __init__(self, table_name):
        self.table_name = table_name
        self.db_url = os.environ.get("DATABASE_URL")

    def get_connection(self):
        if not self.db_url:
            raise ValueError("DATABASE_URL is missing")
        return psycopg2.connect(self.db_url)

    def execute(self, query, params=None):
        """Executes a Write command (INSERT/UPDATE/DELETE)"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(query, params)
                conn.commit()
        finally:
            conn.close()

    def fetch_one(self, query, params=None):
        """Fetches a single row"""
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params)
                return cur.fetchone()
        finally:
            conn.close()

    def search(self, **kwargs):
        # (Your existing search function can stay here if you still use it)
        pass