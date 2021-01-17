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


class VoteViewTests(TestCase):
    def test_no_choice_submit(self):
        article = create_article(
            title="title",
            url="url",
            body="body",
            interest_index=0,
            given_score=50)
        url = reverse('articles:vote', kwargs={"article_id": article.id})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, article.title)
        self.assertContains(response, article.url)
        self.assertContains(response, article.body)
        self.assertContains(response, "好みが選択されずに登録ボタンが押されました")

    def test_no_exists_similar_article(self):
        article = create_article(
            title="title",
            url="url",
            body="body",
            interest_index=0,
            given_score=50)
        url = reverse('articles:vote', kwargs={"article_id": article.id})
        response = self.client.post(
            url, {"name": "preference", "value": "like"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, article.title)
        self.assertContains(response, article.url)
        self.assertContains(response, article.body)
        self.assertNotContains(response, "好み登録に失敗しました")

    def test_no_exists_article(self):
        article = create_article(
            title="title",
            url="url",
            body="body",
            interest_index=0,
            given_score=50)
        url = reverse(
            'articles:vote', kwargs={
                "article_id": article.id + 99999})
        response = self.client.post(
            url, {"name": "preference", "value": "like"})

        self.assertEqual(response.status_code, 404)
