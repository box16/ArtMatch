import os
import re
import MeCab
import requests
import random
from gensim.models.doc2vec import Doc2Vec
from gensim.models.doc2vec import TaggedDocument
from django.core.exceptions import ObjectDoesNotExist
from bs4 import BeautifulSoup
from .models import Article, Interest


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

    def extract_element(self, bs_object, css_selector, is_body=False):
        if not bs_object:
            return ""
        selected_elems = bs_object.select(css_selector)

        if is_body:
            return str(selected_elems[0])

        if (selected_elems is not None) and (len(selected_elems) > 0):
            return '\n'.join([elem.get_text() for elem in selected_elems])
        else:
            return ""

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
    def check_dueto_insert(self, url):
        result = Article.objects.filter(url=url)
        return len(result) == 0

    def escape_single_quote(self, text):
        return re.sub(r"\'", "\'\'", text)

    def insert_article(self, title="", url="", body=""):
        if not self.check_dueto_insert(url):
            return
        if (not title) or (not url) or (not body):
            return

        title = self.escape_single_quote(title)
        body = self.escape_single_quote(body)

        article = Article.objects.create(title=title, url=url, body=body)
        interest = article.interest_set.create()
        article.save()
        interest.save()

    def select_article_pick_one_body_id(self, offset):
        try:
            pick_article = Article.objects.order_by(
                'id')[offset:offset + 1].get()
            return (pick_article.id, pick_article.body)
        except ObjectDoesNotExist:
            return

    def count_articles(self):
        return len(Article.objects.all())

    def update_body(self, url, body):
        article = Article.objects.filter(url=url).update(body=body)

    def select_article_pick_one_url(self, offset):
        try:
            pick_article = Article.objects.order_by(
                'url')[offset:offset + 1].get()
            return pick_article.url
        except ObjectDoesNotExist:
            return


class MyCorpus():
    def __init__(self):
        self.nlp = NLP()
        self.db_api = DBAPI()
        self.pages_num = self.db_api.count_articles()

    def __iter__(self):
        for index in range(self.pages_num):
            pick_article = self.db_api.select_article_pick_one_body_id(index)
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
