import unittest
from ..db_access import DBAccess

class TestDBAccess(unittest.TestCase):
    def setUp(self):
        self.db_access = DBAccess()
    
    def test_check_dueto_insert_true(self):
        dummy_url1 = "https://hogehoge.html"
        dummy_url2 = "https://fugafuga.html"
        with self.db_access._connection.cursor() as cursor:
            cursor.execute(
                f"INSERT INTO articles_articles (id,title,url,body) VALUES (99999,'title','{dummy_url1}','body');")
            self.assertTrue(self.db_access.check_dueto_insert(dummy_url2))

    def test_check_dueto_insert_false(self):
        dummy_url1 = "https://hogehoge.html"
        with self.db_access._connection.cursor() as cursor:
            cursor.execute(
                f"INSERT INTO articles_articles (id,title,url,body) VALUES (99999,'title','{dummy_url1}','body');")
            self.assertFalse(self.db_access.check_dueto_insert(dummy_url1))
    
    def test_escape_single_quote_normal(self):
        text = "ab'cd"
        answer = "ab''cd"
        self.assertEqual(self.db_access.escape_single_quote(text),answer)
    
    def test_escape_single_quote_normal2(self):
        text = "ab''cd"
        answer = "ab''''cd"
        self.assertEqual(self.db_access.escape_single_quote(text),answer)
    
    def test_escape_single_quote_normal3(self):
        text = "abcd"
        answer = "abcd"
        self.assertEqual(self.db_access.escape_single_quote(text),answer)
    
    def test_slect_article_pick_one_body_normal(self):
        body = self.db_access.slect_article_pick_one_body(1)
        self.assertIsNotNone(body)

    def test_slect_article_pick_one_body_overoffset(self):
        body = self.db_access.slect_article_pick_one_body(999999)
        self.assertIsNone(body)

    def test_slect_article_pick_one_body_underoffset(self):
        body = self.db_access.slect_article_pick_one_body(-1)
        self.assertIsNone(body)
    
    def test_slect_article_pick_one_body_zero(self):
        body = self.db_access.slect_article_pick_one_body(0)
        self.assertIsNotNone(body)

    def test_slect_article_pick_one_body_boundary(self):
        body = self.db_access.slect_article_pick_one_body(self.db_access.count_articles())
        self.assertIsNone(body)

    def test_count_articles(self):
        count = self.db_access.count_articles()
        self.assertIsNotNone(count)