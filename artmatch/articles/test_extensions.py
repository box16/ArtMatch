import unittest
import re
from .extensions import D2V
from .extensions import Crawler
from .extensions import DBAccess
from .extensions import NLP

class TestD2V(unittest.TestCase):
    def setUp(self):
        self.d2v = D2V()

    def test_find_similer_articles_normal_id(self):
        result = self.d2v.find_similer_articles(1)
        self.assertIsNotNone(result)
    
    def test_find_similer_articles_over_id(self):
        result = self.d2v.find_similer_articles(999999)
        self.assertIsNone(result)
    
    def test_find_similer_articles_under_id(self):
        result = self.d2v.find_similer_articles(-999999)
        self.assertIsNone(result)

class TestDBAccess(unittest.TestCase):
    def setUp(self):
        self.db_access = DBAccess()
    
    def test_check_dueto_insert_true(self):
        dummy_url1 = "https://hogehoge.html"
        dummy_url2 = "https://fugafuga.html"
        with self.db_access._connection.cursor() as cursor:
            cursor.execute(
                f"INSERT INTO articles_article (id,title,url,body) VALUES (99999,'title','{dummy_url1}','body');")
            self.assertTrue(self.db_access.check_dueto_insert(dummy_url2))

    def test_check_dueto_insert_false(self):
        dummy_url1 = "https://hogehoge.html"
        with self.db_access._connection.cursor() as cursor:
            cursor.execute(
                f"INSERT INTO articles_article (id,title,url,body) VALUES (99999,'title','{dummy_url1}','body');")
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
    
    def test_slect_article_pick_one_body_id_normal(self):
        body = self.db_access.slect_article_pick_one_body_id(1)
        self.assertIsNotNone(body)

    def test_slect_article_pick_one_body_id_overoffset(self):
        body = self.db_access.slect_article_pick_one_body_id(999999)
        self.assertIsNone(body)

    def test_slect_article_pick_one_body_id_underoffset(self):
        body = self.db_access.slect_article_pick_one_body_id(-1)
        self.assertIsNone(body)
    
    def test_slect_article_pick_one_body_id_zero(self):
        body = self.db_access.slect_article_pick_one_body_id(0)
        self.assertIsNotNone(body)

    def test_slect_article_pick_one_body_id_boundary(self):
        body = self.db_access.slect_article_pick_one_body_id(self.db_access.count_articles())
        self.assertIsNone(body)

    def test_count_articles(self):
        count = self.db_access.count_articles()
        self.assertIsNotNone(count)

class TestNLP(unittest.TestCase):
    def setUp(self):
        self.nlp = NLP()

    def test_extract_legal_nouns_verbs_check_nouns(self):
        document = "今日はとても良い天気です"
        result = self.nlp.extract_legal_nouns_verbs(document)

        self.assertIn("今日", result)
        self.assertIn("天気", result)
        self.assertNotIn("は", result)
        self.assertNotIn("とても", result)
        self.assertNotIn("良い", result)
        self.assertNotIn("です", result)

    def test_extract_legal_nouns_verbs_check_verbs(self):
        document = "野球はボールを打って捕って走るスポーツです"
        result = self.nlp.extract_legal_nouns_verbs(document)

        self.assertIn("打つ", result)
        self.assertIn("捕る", result)
        self.assertIn("走る", result)
        self.assertNotIn("て", result)
        self.assertNotIn("は", result)
        self.assertNotIn("を", result)
        self.assertNotIn("です", result)
    
    def test_extract_legal_nouns_verbs_check_unknown(self):
        """現時点では「マウスウォッシュ」が認識されなかった"""
        document = "マウスウォッシュがヤバい"
        result = self.nlp.extract_legal_nouns_verbs(document)

        self.assertNotIn("マウスウォッシュ", result)

class TestWebcraw(unittest.TestCase):
    def setUp(self):
        self.crawler = Crawler()
        self.website = {"name": "PaleolithicMan",
                        "domain": "https://yuchrszk.blogspot.com/",
                        "title_tag": "[class='post-title single-title emfont']",
                        "body_tag": "[class='post-single-body post-body']",
                        "link_collector": re.compile("^(?=https://yuchrszk.blogspot.com/..../.+?)(?!.*archive)(?!.*label).*$"),
                        "link_creater": lambda domestic_url: domestic_url,
                        }

    def test_get_page_normal_url(self):
        bs_object = self.crawler.get_bs_object(self.website["domain"])
        self.assertIsNotNone(bs_object)

    def test_get_page_abnormal_url(self):
        bs_object = self.crawler.get_bs_object("")
        self.assertIsNone(bs_object)

    def test_collect_urls_normal_url(self):
        bs_object = self.crawler.get_bs_object(self.website["domain"])
        urls = self.crawler._collect_urls(bs_object,
                                         self.website["link_collector"])
        self.assertGreater(len(urls), 0)

    def test_collect_urls_abnormal_url(self):
        bs_object = self.crawler.get_bs_object("")
        urls = self.crawler._collect_urls(bs_object,
                                         self.website["link_collector"])
        self.assertEqual(len(urls), 0)

    def test_safe_get_normal_url_title(self):
        bs_object = self.crawler.get_bs_object("https://yuchrszk.blogspot.com/2020/12/20208.html")
        element = self.crawler.extract_element(bs_object,
                                     self.website["title_tag"])
        self.assertIsNotNone(element)

    def test_safe_get_abnormal_url_title(self):
        bs_object = self.crawler.get_bs_object("")
        element = self.crawler.extract_element(bs_object,
                                     self.website["title_tag"])
        self.assertEqual(element, "")
    
    def test_safe_get_normal_url_body(self):
        bs_object = self.crawler.get_bs_object("https://yuchrszk.blogspot.com/2020/12/20208.html")
        element = self.crawler.extract_element(bs_object,
                                        self.website["body_tag"])
        self.assertIsNotNone(element)

    def test_safe_get_abnormal_url_body(self):
        bs_object = self.crawler.get_bs_object("")
        element = self.crawler.extract_element(bs_object,
                                     self.website["body_tag"])
        self.assertEqual(element, "")
    
    def test_format_urls_slash(self):
        urls = ["https://example/"]
        answer_urls = ["https://example"]
        
        result_urls = self.crawler._format_urls(urls)
        self.assertEqual(result_urls, answer_urls)

    def test_format_urls_duplicate(self):
        urls = ["https://example","https://example"]
        answer_urls = ["https://example"]
        
        result_urls = self.crawler._format_urls(urls)
        self.assertEqual(result_urls, answer_urls)

    def test_format_urls_slash_duplicate(self):
        urls = ["https://example/","https://example/"]
        answer_urls = ["https://example"]
        
        result_urls = self.crawler._format_urls(urls)
        self.assertEqual(result_urls, answer_urls)
    
    def test_crawl_normal_url(self):
        urls = self.crawler.crawl_urls(self.website["domain"],
                                  self.website["link_collector"],
                                  times=2)
        self.assertGreater(len(urls), 0)
    
    def test_crawl_abnormal_url(self):
        urls = self.crawler.crawl_urls("",
                                  self.website["link_collector"],
                                  times=2)
        self.assertEqual(len(urls), 0)
    
    def test_crawl_abnormal_times(self):
        urls = self.crawler.crawl_urls(self.website["domain"],
                                  self.website["link_collector"],
                                  times=-2)
        self.assertGreater(len(urls), 0)
        
        urls = self.crawler.crawl_urls(self.website["domain"],
                                  self.website["link_collector"],
                                  times=10000000)
        self.assertGreater(len(urls), 0)