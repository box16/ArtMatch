import re
import math
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from articles.models import Article, Interest, PositiveWord, NegativeWord, Score


class DBAPI:
    def due_to_insert_articles(self, url):
        result = Article.objects.filter(url=url)
        return len(result) == 0

    def escape_single_quote(self, text):
        return re.sub(r"\'", "\'\'", text)

    def insert_article(self, title="", url="", body="",image=""):
        if not self.due_to_insert_articles(url):
            return 0
        if (not title) or (not url) or (not body):
            return 0

        title = self.escape_single_quote(str(title))
        body = self.escape_single_quote(str(body))
        image = str(image)

        article = Article.objects.create(title=title, url=url, body=body,image=image)
        article.save()

        interest = Interest.objects.create(article=article)
        score = Score.objects.create(article=article)
        interest.save()
        score.save()
        return 1

    def select_articles_offset_limit_one(self, offset):
        """id,body,url,titleの順で返す"""
        try:
            pick_article = Article.objects.order_by(
                'id')[offset:offset + 1].get()
            return (
                pick_article.id,
                pick_article.body,
                pick_article.url,
                pick_article.title)
        except ObjectDoesNotExist:
            return
        except AssertionError:
            return

    def count_articles(self):
        return len(Article.objects.all())

    def update_body_from_articles_where_url(self, url, title="",body="",image=""):
        if (not title) or (not body):
            return
        try :
            Article.objects.filter(url=url).update(title=str(title),body=str(body),image=str(image))
            print("update!")
        except TypeError:
            print("update Error!")
            return

    def select_id_from_articles_sort_limit_top_twenty(self, positive=True):
        max_articles_num = math.ceil(self.count_articles() * 0.2)
        if positive:
            return [interest.article_id for interest in Interest.objects.order_by(
                "interest_index").reverse().filter(interest_index__gt=0)[:max_articles_num]]
        else:
            return [interest.article_id for interest in Interest.objects.order_by(
                "interest_index").filter(interest_index__lt=0)[:max_articles_num]]

    def select_id_from_articles_where_interest_index_zero(self):
        return [
            interest.article_id for interest in Interest.objects.all().filter(
                interest_index=0)]

    def select_body_from_articles_where_id(self, id):
        try:
            return Article.objects.filter(id=id).get().body
        except Article.DoesNotExist:
            return ""

    def insert_word(self, word, positive=True):
        table = PositiveWord if positive else NegativeWord
        try:
            positive_word = table.objects.create(word=word)
            positive_word.save()
            return 1
        except IntegrityError:
            return 0

    def check_already_exists_word(self, word, positive=True):
        table = PositiveWord if positive else NegativeWord
        result = table.objects.filter(word=word)
        return len(result) > 0

    def select_word(self, positive=True):
        table = PositiveWord if positive else NegativeWord
        return [_object.word for _object in table.objects.all()]

    def update_score_where_article_id(self, article_id, given_score):
        try:
            article = Article.objects.get(pk=article_id)
            _score = Score.objects.get(article__pk=article_id)
            _score.score = given_score
            _score.save()
            return 1
        except Article.DoesNotExist:
            return 0
        except Score.DoesNotExist:
            Score.objects.create(article=article, score=given_score)
            return 1

    def select_recommend_articles(self):
        recommend_articles = Article.objects.filter(
            score__score__gt=50).filter(
            interest__interest_index__lt=1).filter(
            interest__interest_index__gt=-
            1)
        if len(recommend_articles) < 10:
            return Article.objects.all()[:20]
        else:
            return recommend_articles[:20]

