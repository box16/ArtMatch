from django.test import TestCase
from articles.extensions.db_api import DBAPI
from articles.models import Article, Interest, Score


def create_article(
        title="title",
        url="url",
        body="body",
        interest_index=None,
        given_score=None):
    article = Article.objects.create(title=title, url=url, body=body)
    article.save()

    if interest_index is not None:
        interest = Interest.objects.create(
            article=article,
            interest_index=interest_index)
        interest.save()
    if given_score is not None:
        _score = Score.objects.create(
            article=article,
            score=given_score)
        _score.save()

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

        self.api.update_body_from_articles_where_url(
            "url1", title="changed_title", body="changed_body", image="")
        pick = self.api.select_articles_offset_limit_one(0)
        self.assertIsNotNone(pick)
        self.assertEqual(pick[1], "changed_body")
        self.assertEqual(pick[3], "changed_title")

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

    def test_select_word(self):
        self.api.insert_word("posi1", positive=True)
        self.api.insert_word("posi2", positive=True)
        self.api.insert_word("posi3", positive=True)
        self.assertListEqual(
            self.api.select_word(
                positive=True), [
                "posi1", "posi2", "posi3"])

        self.api.insert_word("nega1", positive=False)
        self.api.insert_word("nega2", positive=False)
        self.api.insert_word("nega3", positive=False)
        self.assertListEqual(
            self.api.select_word(
                positive=False), [
                "nega1", "nega2", "nega3"])

    def test_update_score_where_article_id_normal(self):
        self.api.insert_article(title="title1", url="url1", body="body1")
        article = self.api.select_articles_offset_limit_one(0)

        self.assertEqual(Score.objects.get(article__pk=article[0]).score, 50)

        self.api.update_score_where_article_id(article[0], 60)
        self.assertEqual(Score.objects.get(article__pk=article[0]).score, 60)

    def test_update_score_where_article_id_no_article(self):
        self.api.insert_article(title="title1", url="url1", body="body1")
        article = self.api.select_articles_offset_limit_one(0)

        result = self.api.update_score_where_article_id(article[0] + 99, 60)
        self.assertEqual(result, 0)

    def test_update_score_where_article_id_no_score(self):
        create_article(
            title="title1",
            url="url1",
            body="body1",
            interest_index=1)
        article = self.api.select_articles_offset_limit_one(0)
        result = self.api.update_score_where_article_id(article[0], 60)
        self.assertEqual(result, 1)
        self.assertEqual(Score.objects.get(article__pk=article[0]).score, 60)
