import unittest
import re
from django.test import TestCase
from django.urls import reverse
from .extensions import D2V
from .extensions import Crawler
from .extensions import NLP
from .extensions import DBAPI
from .models import Article, Interest


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
        self.website = {
            "name": "PaleolithicMan",
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
        bs_object = self.crawler.get_bs_object(
            "https://yuchrszk.blogspot.com/2020/12/20208.html")
        element = self.crawler.extract_element(bs_object,
                                               self.website["title_tag"])
        self.assertIsNotNone(element)

    def test_safe_get_abnormal_url_title(self):
        bs_object = self.crawler.get_bs_object("")
        element = self.crawler.extract_element(bs_object,
                                               self.website["title_tag"])
        self.assertEqual(element, "")

    def test_safe_get_normal_url_body(self):
        bs_object = self.crawler.get_bs_object(
            "https://yuchrszk.blogspot.com/2020/12/20208.html")
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
        urls = ["https://example", "https://example"]
        answer_urls = ["https://example"]

        result_urls = self.crawler._format_urls(urls)
        self.assertEqual(result_urls, answer_urls)

    def test_format_urls_slash_duplicate(self):
        urls = ["https://example/", "https://example/"]
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


def create_article(title="title", url="url", body="body"):
    return Article.objects.create(title=title, url=url, body=body)


class TestDBAPI(TestCase):
    def setUp(self):
        self.api = DBAPI()

    def test_check_dueto_insert(self):
        article = create_article()
        self.assertFalse(self.api.check_dueto_insert("url"))
        self.assertTrue(self.api.check_dueto_insert("sample"))

    def test_escape_single_quote_normal(self):
        text = "ab'cd"
        answer = "ab''cd"
        self.assertEqual(self.api.escape_single_quote(text), answer)

        text = "ab''cd"
        answer = "ab''''cd"
        self.assertEqual(self.api.escape_single_quote(text), answer)

        text = "abcd"
        answer = "abcd"
        self.assertEqual(self.api.escape_single_quote(text), answer)

    def test_insert_article_normal(self):
        self.api.insert_article(title="title", url="url", body="body")
        self.assertIsNotNone(Article.objects.all())
        self.assertIsNotNone(Interest.objects.all())

    def test_insert_article_missing_element(self):
        self.api.insert_article(title="", url="url", body="body")
        self.assertEqual(len(Article.objects.all()), 0)
        self.assertEqual(len(Interest.objects.all()), 0)

        self.api.insert_article(title="title", url="", body="body")
        self.assertEqual(len(Article.objects.all()), 0)
        self.assertEqual(len(Interest.objects.all()), 0)

        self.api.insert_article(title="title", url="url", body="")
        self.assertEqual(len(Article.objects.all()), 0)
        self.assertEqual(len(Interest.objects.all()), 0)

        self.api.insert_article(title="", url="url", body="body")
        self.assertEqual(len(Article.objects.all()), 0)
        self.assertEqual(len(Interest.objects.all()), 0)

        self.api.insert_article(title="title", url="", body="body")
        self.assertEqual(len(Article.objects.all()), 0)
        self.assertEqual(len(Interest.objects.all()), 0)

        self.api.insert_article(title="", url="", body="")
        self.assertEqual(len(Article.objects.all()), 0)
        self.assertEqual(len(Interest.objects.all()), 0)

    def test_insert_article_already_url(self):
        self.api.insert_article(title="title", url="url", body="body")
        self.api.insert_article(title="title2", url="url", body="body2")
        self.assertEqual(len(Article.objects.all()), 1)
        self.assertEqual(len(Interest.objects.all()), 1)

    def test_insert_article_already_url_can_insert(self):
        self.api.insert_article(title="title", url="url", body="body")
        self.api.insert_article(title="title", url="url1", body="body")
        self.assertEqual(len(Article.objects.all()), 2)
        self.assertEqual(len(Interest.objects.all()), 2)

    def test_select_article_pick_one_body_id_normal(self):
        self.api.insert_article(title="title1", url="url1", body="body1")
        self.api.insert_article(title="title2", url="url2", body="body2")

        pick1 = self.api.select_article_pick_one_body_id(0)
        self.assertIsNotNone(pick1[0])
        self.assertEqual(pick1[1], "body1")

        pick2 = self.api.select_article_pick_one_body_id(1)
        self.assertIsNotNone(pick2[0])
        self.assertEqual(pick2[1], "body2")

    def test_select_article_pick_one_body_id_over_offset(self):
        self.api.insert_article(title="title1", url="url1", body="body1")
        self.api.insert_article(title="title2", url="url2", body="body2")

        pick = self.api.select_article_pick_one_body_id(99)
        self.assertIsNone(pick)

    def test_count_articles_normal(self):
        self.api.insert_article(title="title1", url="url1", body="body1")
        self.api.insert_article(title="title2", url="url2", body="body2")

        self.assertEqual(self.api.count_articles(), 2)

    def test_count_articles_zero(self):
        self.assertEqual(self.api.count_articles(), 0)


class IndexViewTests(TestCase):
    def test_no_articles(self):
        response = self.client.get(reverse('articles:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No articles are available.")
        self.assertQuerysetEqual(response.context['pick_up_articles'], [])

    def test_has_articles(self):
        a = create_article()
        response = self.client.get(reverse('articles:index'))
        self.assertQuerysetEqual(
            response.context['pick_up_articles'],
            ['<Article: title>']
        )


class DetailViewTests(TestCase):
    def test_normal_access(self):
        a = create_article()
        url = reverse('articles:detail', args=(a.id,))
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, a.title)
        self.assertContains(response, a.url)
        self.assertContains(response, a.body)
        self.assertContains(response, "記事一覧に戻る")

    def test_abnormal_access(self):
        a = create_article()
        url = reverse('articles:detail', args=(a.id + 999999,))
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)
