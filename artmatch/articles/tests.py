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


def create_article(title="title", url="url", body="body", interest_index=0):
    article = Article.objects.create(title=title, url=url, body=body)
    interest = Interest.objects.create(
        article_id=article.id,
        interest_index=interest_index)
    article.save()
    interest.save()
    return article


class TestDBAPI(TestCase):
    def setUp(self):
        self.api = DBAPI()

    def test_due_to_insert_articles(self):
        article = create_article()
        self.assertFalse(self.api.due_to_insert_articles("url"))
        self.assertTrue(self.api.due_to_insert_articles("sample"))

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

    def test_select_articles_offset_limit_one_id_body_normal(self):
        create_article(
            title="title1",
            url="url1",
            body="body1",
            interest_index=0)
        create_article(
            title="title2",
            url="url2",
            body="body2",
            interest_index=0)

        pick1 = self.api.select_articles_offset_limit_one(0)
        self.assertIsNotNone(pick1[0])
        self.assertEqual(pick1[1], "body1")

        pick2 = self.api.select_articles_offset_limit_one(1)
        self.assertIsNotNone(pick2[0])
        self.assertEqual(pick2[1], "body2")

    def test_select_articles_offset_limit_one_id_body_over_offset(self):
        create_article(
            title="title1",
            url="url1",
            body="body1",
            interest_index=0)
        create_article(
            title="title2",
            url="url2",
            body="body2",
            interest_index=0)

        pick = self.api.select_articles_offset_limit_one(99)
        self.assertIsNone(pick)

    def test_select_articles_offset_limit_one_id_body_under_offset(self):
        create_article(
            title="title1",
            url="url1",
            body="body1",
            interest_index=0)
        create_article(
            title="title2",
            url="url2",
            body="body2",
            interest_index=0)

        pick = self.api.select_articles_offset_limit_one(-1)
        self.assertIsNone(pick)

    def test_select_articles_offset_limit_one_url_normal(self):
        create_article(
            title="title1",
            url="url1",
            body="body1",
            interest_index=0)
        create_article(
            title="title2",
            url="url2",
            body="body2",
            interest_index=0)

        pick1 = self.api.select_articles_offset_limit_one(0)[2]
        self.assertIsNotNone(pick1)
        self.assertEqual(pick1, "url1")

        pick2 = self.api.select_articles_offset_limit_one(1)[2]
        self.assertIsNotNone(pick2[0])
        self.assertEqual(pick2, "url2")

    def test_select_articles_offset_limit_one_url_over_offset(self):
        create_article(
            title="title1",
            url="url1",
            body="body1",
            interest_index=0)
        create_article(
            title="title2",
            url="url2",
            body="body2",
            interest_index=0)

        pick = self.api.select_articles_offset_limit_one(99)
        self.assertIsNone(pick)

    def test_select_articles_offset_limit_one_url_under_offset(self):
        create_article(
            title="title1",
            url="url1",
            body="body1",
            interest_index=0)
        create_article(
            title="title2",
            url="url2",
            body="body2",
            interest_index=0)

        pick = self.api.select_articles_offset_limit_one(-1)
        self.assertIsNone(pick)

    def test_count_articles_normal(self):
        create_article(
            title="title1",
            url="url1",
            body="body1",
            interest_index=0)
        create_article(
            title="title2",
            url="url2",
            body="body2",
            interest_index=0)

        self.assertEqual(self.api.count_articles(), 2)

    def test_count_articles_zero(self):
        self.assertEqual(self.api.count_articles(), 0)

    def test_update_body_from_articles_where_url(self):
        self.api.insert_article(title="title1", url="url1", body="body1")
        pick = self.api.select_articles_offset_limit_one(0)
        self.assertIsNotNone(pick)
        self.assertEqual(pick[1], "body1")

        self.api.update_body_from_articles_where_url("url1", "changed")
        pick = self.api.select_articles_offset_limit_one(0)
        self.assertIsNotNone(pick)
        self.assertEqual(pick[1], "changed")

    def test_select_id_from_articles_sort_limit_top_twenty_lower_limit(self):
        create_article(
            title="title1",
            url="url1",
            body="body1",
            interest_index=1)
        create_article(
            title="title2",
            url="url2",
            body="body2",
            interest_index=-1)

        ids = self.api.select_id_from_articles_sort_limit_top_twenty(
            positive=True)
        self.assertEqual(len(ids), 1)

        ids = self.api.select_id_from_articles_sort_limit_top_twenty(
            positive=False)
        self.assertEqual(len(ids), 1)

    def test_select_id_from_articles_sort_limit_top_twenty_positive_max_num(
            self):
        create_article(
            title="title",
            url="url1",
            body="body",
            interest_index=1)
        create_article(
            title="title",
            url="url2",
            body="body",
            interest_index=1)
        create_article(
            title="title",
            url="url3",
            body="body",
            interest_index=1)
        create_article(
            title="title",
            url="url4",
            body="body",
            interest_index=1)
        create_article(
            title="title",
            url="url5",
            body="body",
            interest_index=1)
        create_article(
            title="title",
            url="url6",
            body="body",
            interest_index=1)
        create_article(
            title="title",
            url="url7",
            body="body",
            interest_index=1)
        create_article(
            title="title",
            url="url8",
            body="body",
            interest_index=1)
        create_article(
            title="title",
            url="url9",
            body="body",
            interest_index=1)
        create_article(
            title="title",
            url="url0",
            body="body",
            interest_index=1)

        ids = self.api.select_id_from_articles_sort_limit_top_twenty(
            positive=True)
        self.assertEqual(len(ids), 2)

        ids = self.api.select_id_from_articles_sort_limit_top_twenty(
            positive=False)
        self.assertEqual(len(ids), 0)

    def test_select_id_from_articles_sort_limit_top_twenty_negative_max_num(
            self):
        create_article(
            title="title",
            url="url1",
            body="body",
            interest_index=-1)
        create_article(
            title="title",
            url="url2",
            body="body",
            interest_index=-1)
        create_article(
            title="title",
            url="url3",
            body="body",
            interest_index=-1)
        create_article(
            title="title",
            url="url4",
            body="body",
            interest_index=-1)
        create_article(
            title="title",
            url="url5",
            body="body",
            interest_index=-1)
        create_article(
            title="title",
            url="url6",
            body="body",
            interest_index=-1)
        create_article(
            title="title",
            url="url7",
            body="body",
            interest_index=-1)
        create_article(
            title="title",
            url="url8",
            body="body",
            interest_index=-1)
        create_article(
            title="title",
            url="url9",
            body="body",
            interest_index=-1)
        create_article(
            title="title",
            url="url0",
            body="body",
            interest_index=-1)

        ids = self.api.select_id_from_articles_sort_limit_top_twenty(
            positive=True)
        self.assertEqual(len(ids), 0)

        ids = self.api.select_id_from_articles_sort_limit_top_twenty(
            positive=False)
        self.assertEqual(len(ids), 2)

    def test_select_id_from_articles_where_interest_index_zero_normal(self):
        create_article(
            title="title1",
            url="url1",
            body="body1",
            interest_index=1)
        create_article(
            title="title2",
            url="url2",
            body="body2",
            interest_index=0)

        ids = self.api.select_id_from_articles_where_interest_index_zero()
        self.assertEqual(len(ids), 1)

    def test_select_id_from_articles_where_interest_index_zero_abnormal(self):
        create_article(
            title="title1",
            url="url1",
            body="body1",
            interest_index=1)
        create_article(
            title="title2",
            url="url2",
            body="body2",
            interest_index=-1)

        ids = self.api.select_id_from_articles_where_interest_index_zero()
        self.assertEqual(len(ids), 0)

    def test_select_body_from_articles_where_id_normal(self):
        article = create_article(
            title="title1",
            url="url1",
            body="body1",
            interest_index=1)
        body = self.api.select_body_from_articles_where_id(article.id)
        self.assertEqual(body, "body1")

    def test_select_body_from_articles_where_id_over(self):
        article = create_article(
            title="title1",
            url="url1",
            body="body1",
            interest_index=1)
        body = self.api.select_body_from_articles_where_id(article.id + 99)
        self.assertEqual(body, "")

    def test_select_body_from_articles_where_id_under(self):
        article = create_article(
            title="title1",
            url="url1",
            body="body1",
            interest_index=1)
        body = self.api.select_body_from_articles_where_id(-1)
        self.assertEqual(body, "")

    def test_insert_positive_word(self):
        self.assertEqual(self.api.insert_word("sample", positive=True), 1)
        self.assertEqual(self.api.insert_word("sample", positive=True), 0)

    def test_insert_negative_word(self):
        self.assertEqual(self.api.insert_word("sample", positive=False), 1)
        self.assertEqual(self.api.insert_word("sample", positive=False), 0)

    def test_check_already_exists_positive_word(self):
        self.api.insert_word("sample", positive=True)
        self.assertTrue(
            self.api.check_already_exists_word(
                "sample", positive=True))
        self.assertFalse(
            self.api.check_already_exists_word("1sample1", positive=True))

    def test_check_already_exists_negative_word(self):
        self.api.insert_word("sample", positive=False)
        self.assertTrue(
            self.api.check_already_exists_word(
                "sample", positive=False))
        self.assertFalse(
            self.api.check_already_exists_word("1sample1", positive=False))


class IndexViewTests(TestCase):
    def test_no_articles(self):
        response = self.client.get(reverse('articles:index'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "好み未登録の記事はありません")
        self.assertContains(response, "おすすめ記事はありません")
        self.assertQuerysetEqual(
            response.context['no_preference_articles'].values(), [])
        self.assertQuerysetEqual(
            response.context['recommend_articles'].values(), [])

    def test_has_articles_interest_zero(self):
        a = create_article()
        response = self.client.get(reverse('articles:index'))

        self.assertNotContains(response, "好み未登録の記事はありません")
        self.assertContains(response, "おすすめ記事はありません")
        self.assertQuerysetEqual(
            response.context['no_preference_articles'].values(),
            ['<Article: title>'])
        self.assertQuerysetEqual(
            response.context['recommend_articles'].values(), [])

    def test_has_articles_interest_greater_zero(self):
        a = create_article(interest_index=1)
        response = self.client.get(reverse('articles:index'))

        self.assertContains(response, "好み未登録の記事はありません")
        self.assertNotContains(response, "おすすめ記事はありません")
        self.assertQuerysetEqual(
            response.context['no_preference_articles'].values(), [])
        self.assertQuerysetEqual(
            response.context['recommend_articles'].values(),
            ['<Article: title>'])

    def test_has_articles_interest_greater_zero_zero(self):
        a0 = create_article(
            title="title0",
            url="url0",
            body="body0",
            interest_index=0)
        a1 = create_article(
            title="title1",
            url="url1",
            body="body1",
            interest_index=1)
        response = self.client.get(reverse('articles:index'))

        self.assertNotContains(response, "好み未登録の記事はありません")
        self.assertNotContains(response, "おすすめ記事はありません")
        self.assertQuerysetEqual(
            response.context['no_preference_articles'].values(),
            ['<Article: title0>'])
        self.assertQuerysetEqual(
            response.context['recommend_articles'].values(),
            ['<Article: title1>'])

    def test_has_articles_interest_less_zero(self):
        a = create_article(interest_index=-1)
        response = self.client.get(reverse('articles:index'))

        self.assertContains(response, "好み未登録の記事はありません")
        self.assertContains(response, "おすすめ記事はありません")
        self.assertQuerysetEqual(
            response.context['no_preference_articles'].values(), [])
        self.assertQuerysetEqual(
            response.context['recommend_articles'].values(), [])

    def test_has_articles_interest_less_zero_zero(self):
        a0 = create_article(
            title="title0",
            url="url0",
            body="body0",
            interest_index=0)
        a1 = create_article(
            title="title1",
            url="url1",
            body="body1",
            interest_index=-1)
        response = self.client.get(reverse('articles:index'))

        self.assertNotContains(response, "好み未登録の記事はありません")
        self.assertContains(response, "おすすめ記事はありません")
        self.assertQuerysetEqual(
            response.context['no_preference_articles'].values(),
            ['<Article: title0>'])
        self.assertQuerysetEqual(
            response.context['recommend_articles'].values(), [])


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
        self.assertContains(response, "類似記事")
        self.assertContains(response, "好み登録")

    def test_abnormal_access(self):
        a = create_article()
        url = reverse('articles:detail', args=(a.id + 999999,))
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)


class VoteViewTests(TestCase):
    def test_no_choice_submit(self):
        a = create_article()
        url = reverse('articles:vote', kwargs={"article_id": a.id})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, a.title)
        self.assertContains(response, a.url)
        self.assertContains(response, a.body)
        self.assertContains(response, "好みが選択されずに登録ボタンが押されました")

    def test_no_exists_similar_article(self):
        a = create_article()
        url = reverse('articles:vote', kwargs={"article_id": a.id})
        response = self.client.post(
            url, {"name": "preference", "value": "like"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, a.title)
        self.assertContains(response, a.url)
        self.assertContains(response, a.body)
        self.assertNotContains(response, "好み登録に失敗しました")

    def test_no_exists_article(self):
        a = create_article()
        url = reverse('articles:vote', kwargs={"article_id": a.id + 99999})
        response = self.client.post(
            url, {"name": "preference", "value": "like"})

        self.assertEqual(response.status_code, 404)
