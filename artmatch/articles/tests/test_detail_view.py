from django.test import TestCase
from articles.extensions.db_api import DBAPI
from django.urls import reverse
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

class DetailViewTests(TestCase):
    def test_normal_access(self):
        article = create_article(
            title="title",
            url="url",
            body="body",
            interest_index=0,
            given_score=50)
        url = reverse('articles:detail', args=(article.id,))
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, article.title)
        self.assertContains(response, article.url)
        self.assertContains(response, article.body)
        self.assertContains(response, "記事一覧に戻る")
        self.assertContains(response, "類似記事")
        self.assertContains(response, "好み登録")

    def test_abnormal_access(self):
        article = create_article(
            title="title",
            url="url",
            body="body",
            interest_index=0,
            given_score=50)
        url = reverse('articles:detail', args=(article.id + 999999,))
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)