import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

class DBConnector:
    @staticmethod
    def get_connection():
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            port=os.getenv('DB_PORT'),
            password=os.getenv('DB_PASSWORD'),
            cursor_factory=RealDictCursor,

        )
        conn.autocommit = True
        return conn
