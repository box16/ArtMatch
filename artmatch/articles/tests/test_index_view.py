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

class IndexViewTests(TestCase):
    def test_no_articles(self):
        response = self.client.get(reverse('articles:index'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "おすすめ記事はありません")
        self.assertQuerysetEqual(
            response.context['recommend_articles'].values(), [])

    def test_has_articles_score60_interest0(self):
        """おすすめが表示される"""
        article = create_article(
            title="title",
            url="url",
            body="body",
            interest_index=0,
            given_score=60)
        response = self.client.get(reverse('articles:index'))

        self.assertNotContains(response, "おすすめ記事はありません")
        self.assertQuerysetEqual(
            response.context['recommend_articles'],
            ['<Article: title>'])

    def test_has_articles_score60_interest1(self):
        """とりあえず表示される"""
        article = create_article(
            title="title",
            url="url",
            body="body",
            interest_index=1,
            given_score=60)
        response = self.client.get(reverse('articles:index'))

        self.assertNotContains(response, "おすすめ記事はありません")
        self.assertQuerysetEqual(
            response.context['recommend_articles'],
            ['<Article: title>'])

    def test_has_articles_score60_interestm1(self):
        """とりあえず表示される"""
        article = create_article(
            title="title",
            url="url",
            body="body",
            interest_index=-1,
            given_score=60)
        response = self.client.get(reverse('articles:index'))

        self.assertNotContains(response, "おすすめ記事はありません")
        self.assertQuerysetEqual(
            response.context['recommend_articles'],
            ['<Article: title>'])

    def test_has_articles_score40_interest0(self):
        """とりあえず表示される"""
        article = create_article(
            title="title",
            url="url",
            body="body",
            interest_index=0,
            given_score=40)
        response = self.client.get(reverse('articles:index'))

        self.assertNotContains(response, "おすすめ記事はありません")
        self.assertQuerysetEqual(
            response.context['recommend_articles'],
            ['<Article: title>'])

    def test_has_articles_score40_interest1(self):
        """とりあえず表示される"""
        article = create_article(
            title="title",
            url="url",
            body="body",
            interest_index=1,
            given_score=40)
        response = self.client.get(reverse('articles:index'))

        self.assertNotContains(response, "おすすめ記事はありません")
        self.assertQuerysetEqual(
            response.context['recommend_articles'],
            ['<Article: title>'])


    def test_has_articles_score40_interestm1(self):
        """とりあえず表示される"""
        article = create_article(
            title="title",
            url="url",
            body="body",
            interest_index=-1,
            given_score=40)
        response = self.client.get(reverse('articles:index'))
        self.assertNotContains(response, "おすすめ記事はありません")
        self.assertQuerysetEqual(
            response.context['recommend_articles'],
            ['<Article: title>'])
