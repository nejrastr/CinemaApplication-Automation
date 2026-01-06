import psycopg2
from psycopg2.extras import RealDictCursor
import os

class DBConnector:
    @staticmethod
    def get_connection():
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'cinebh'),
            user=os.getenv('DB_USER', 'nejra'),
            port=os.getenv('DB_PORT', '5432'),
            password=os.getenv('DB_PASSWORD', ''),
            cursor_factory=RealDictCursor,

        )
        conn.autocommit = True
        return conn
