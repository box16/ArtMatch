import os
import re
import MeCab
import requests
import random
import math
from gensim.models.doc2vec import Doc2Vec
from gensim.models.doc2vec import TaggedDocument
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from bs4 import BeautifulSoup
from .models import Article, Interest, PositiveWord, NegativeWord, Score


class Crawler:
    def __init__(self):
        pass

    def get_bs_object(self, url):
        try:
            req = requests.get(url)
        except requests.exceptions.RequestException:
            return None
        return BeautifulSoup(req.text, "html.parser")

    def _collect_urls(self, bs_object, link_collector):
        if not bs_object:
            return []
        result_urls = []
        for link in bs_object.find_all("a", href=link_collector):
            if not link.attrs["href"]:
                continue
            result_urls.append(link.attrs["href"])
        return list(set(result_urls))

    def extract_element(self, bs_object, title_selector, body_selector):
        if not bs_object:
            return None
        
        try:
            title = bs_object.select(title_selector)[0].get_text()
            body = bs_object.select(body_selector)[0]
        except IndexError:
            return None
        
        try:
            image = bs_object.select(body_selector+ " img")[0].attrs["src"]
        except IndexError:
            return {"title":title,
                "body" :body,
                "image" :"",
            }

        return {"title":title,
                "body" :body,
                "image" :image,
               }

    def _format_urls(self, urls):
        for index, url in enumerate(urls):
            urls[index] = re.sub(r"/$", "", url)
        return list(set(urls))

    def crawl_urls(self, domain, link_collector, times=20):
        base_url = domain
        progress = 0
        urls = []
        if (times <= 0) or (times >= 100):
            times = 2
        while progress < times:
            bs_object = self.get_bs_object(base_url)
            if not bs_object:
                break
            urls = urls + self._collect_urls(bs_object, link_collector)
            urls = self._format_urls(urls)
            base_url = random.choice(urls)
            progress += 1
        return urls


class NLP():
    def __init__(self):
        path = os.environ.get("MECABDIC")
        self._mecab_dic = MeCab.Tagger(f'--unk-feature "unknown" -d {path}')
        self._mecab_dic.parse("")

    def extract_legal_nouns_verbs(self, document):
        token = self._mecab_dic.parseToNode(document)
        result = []
        while token:
            if token.feature == "unknown":
                token = token.next
                continue
            part = token.feature.split(",")[0]
            origin = token.feature.split(",")[6]
            if (part == "名詞") or (part == "動詞"):
                result.append(origin)
            token = token.next
        return result


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
            article = Article.objects.filter(url=url).update(title=str(title),body=str(body),image=str(image))
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


class MyCorpus():
    def __init__(self):
        self.nlp = NLP()
        self.db_api = DBAPI()
        self.pages_num = self.db_api.count_articles()

    def __iter__(self):
        for index in range(self.pages_num):
            pick_article = self.db_api.select_articles_offset_limit_one(index)
            body = self.nlp.extract_legal_nouns_verbs(pick_article[1])
            yield TaggedDocument(words=body, tags=[pick_article[0]])


class D2V():
    def __init__(self):
        self.path = os.environ.get("CORPUSDIR")
        try:
            self.model = Doc2Vec.load(self.path + "d2v.model")
        except FileNotFoundError:
            self.model = None

    def training(self):
        corpus = MyCorpus()
        model = Doc2Vec(
            documents=corpus,
            dm=1,
            vector_size=300,
            window=8,
            min_count=10,
            workers=4)
        del(corpus)
        model.save(self.path + "d2v.model")
        self.__init__()

    def find_similer_articles(self, id):
        try:
            return self.model.docvecs.most_similar(
                positive={
                    id,
                },
                topn=10)
        except KeyError:  # over idの時にKeyError
            return None
        except IndexError:  # かなりunder idの時にIndexError
            return None
