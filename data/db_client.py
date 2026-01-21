class DBClient:
    def __init__(self, db_connection):
        self.db = db_connection

    def fetch_one(self, query):
        with self.db.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchone()

    def fetch_all(self, query):
        with self.db.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()