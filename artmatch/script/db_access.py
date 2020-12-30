import psycopg2
import os

class DBAccess:
    def __init__(self):
        database_info = os.environ.get("ARTMATCHDB")
        self._connection = psycopg2.connect(database_info)

    def check_dueto_insert(self, url):
        with self._connection.cursor() as cursor:
            cursor.execute(f"SELECT url FROM articles_articles WHERE url='{url}';")
            result = cursor.fetchall()
            if result:
                return False
            else:
                return True