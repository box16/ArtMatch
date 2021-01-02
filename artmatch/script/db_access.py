import psycopg2
import os
import re

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
    
    def escape_single_quote(self,text):
        return re.sub(r"\'", "\'\'", text)
    
    def insert_article(self,title="",url="",body=""):
        """commit 入ってくるとテストが難しいため、テスト未作成"""
        if not self.check_dueto_insert(url):
            return
        if (not title) or (not url) or (not body):
            return
        title = self.escape_single_quote(title)
        body = self.escape_single_quote(body)
        with self._connection.cursor() as cursor:
            cursor.execute(f"INSERT INTO articles_articles (id,title,url,body) VALUES (nextval('articles_articles_id_seq'),'{title}','{url}','{body}');")
            self._connection.commit()

    def slect_article_pick_one_body(self,offset):
        with self._connection.cursor() as cursor:
            if (offset >= self.count_articles()) or (offset < 0):
                return None
            cursor.execute(f"SELECT body FROM articles_articles OFFSET {offset} LIMIT 1;")
            return cursor.fetchone()[0]
    
    def count_articles(self):
        with self._connection.cursor() as cursor:
            cursor.execute(f"SELECT count(body) FROM articles_articles;")
            return cursor.fetchone()[0]