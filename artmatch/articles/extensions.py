import psycopg2
import os
import re
import MeCab
import requests
import random
from gensim.models.doc2vec import Doc2Vec
from gensim.models.doc2vec import TaggedDocument
from bs4 import BeautifulSoup

class Crawler:
    def __init__(self):
        pass

    def get_bs_object(self, url):
        try:
            req = requests.get(url)
        except requests.exceptions.RequestException:
            return None
        return BeautifulSoup(req.text, "html.parser")
    
    def _collect_urls(self,bs_object,link_collector):
        if not bs_object:
            return []
        result_urls = []
        for link in bs_object.find_all("a", href=link_collector):
            if not link.attrs["href"]:
                continue
            result_urls.append(link.attrs["href"])
        return list(set(result_urls))

    def extract_element(self, bs_object, css_selector):
        if not bs_object:
            return ""
        selected_elems = bs_object.select(css_selector)
        if (selected_elems is not None) and (len(selected_elems) > 0):
            return '\n'.join([elem.get_text() for elem in selected_elems])
        else:
            return ""
    
    def _format_urls(self,urls):
        for index,url in enumerate(urls):
            urls[index] = re.sub(r"/$", "", url)
        return list(set(urls))
    
    def crawl_urls(self,domain,link_collector,times=20):
        base_url = domain
        progress = 0
        urls = []
        if (times <= 0) or (times >= 100):
            times = 2
        while progress < times:
            bs_object = self.get_bs_object(base_url)
            if not bs_object:
                break
            urls = urls + self._collect_urls(bs_object,link_collector)
            urls = self._format_urls(urls)
            base_url = random.choice(urls)
            progress += 1
        return urls

class NLP():
    def __init__(self):
        path = os.environ.get("MECABDIC")
        self._mecab_dic = MeCab.Tagger(f'--unk-feature "unknown" -d {path}')
        self._mecab_dic.parse("")
    
    def extract_legal_nouns_verbs(self,document):
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

class DBAccess:
    def __init__(self):
        database_info = os.environ.get("ARTMATCHDB")
        self._connection = psycopg2.connect(database_info)

    def check_dueto_insert(self, url):
        with self._connection.cursor() as cursor:
            cursor.execute(f"SELECT url FROM articles_articles WHERE url='{url}';")
            result = cursor.fetchall()
            if result:
                return False
            else:
                return True
    
    def escape_single_quote(self,text):
        return re.sub(r"\'", "\'\'", text)
    
    def insert_article(self,title="",url="",body=""):
        """commit 入ってくるとテストが難しいため、テスト未作成"""
        if not self.check_dueto_insert(url):
            return
        if (not title) or (not url) or (not body):
            return
        title = self.escape_single_quote(title)
        body = self.escape_single_quote(body)
        with self._connection.cursor() as cursor:
            cursor.execute(f"INSERT INTO articles_articles (id,title,url,body) VALUES (nextval('articles_articles_id_seq'),'{title}','{url}','{body}');")
            self._connection.commit()

    def slect_article_pick_one_body_id(self,offset):
        with self._connection.cursor() as cursor:
            if (offset >= self.count_articles()) or (offset < 0):
                return None
            cursor.execute(f"SELECT id,body FROM articles_articles OFFSET {offset} LIMIT 1;")
            return cursor.fetchone()
    
    def count_articles(self):
        with self._connection.cursor() as cursor:
            cursor.execute(f"SELECT count(body) FROM articles_articles;")
            return cursor.fetchone()[0]

class MyCorpus():
    def __init__(self):
        self.nlp = NLP()
        self.db_access = DBAccess()
        self.pages_num = self.db_access.count_articles()

    def __iter__(self):
        for index in range(self.pages_num):
            pick_article = self.db_access.slect_article_pick_one_body_id(index)
            body = self.nlp.extract_legal_nouns_verbs(pick_article[1])
            yield TaggedDocument(words=body, tags=[pick_article[0]])

class D2V():
    def __init__(self):
        self.path = os.environ.get("CORPUSDIR")
        try:
            self.model = Doc2Vec.load(self.path+"d2v.model")
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
        model.save(self.path+"d2v.model")
        self.__init__()
    
    def find_similer_articles(self,id):
        try:
            return [id for id,similality in self.model.docvecs.most_similar(positive={id, }, topn=5)]
        except KeyError:#over idの時にKeyError
            return None
        except IndexError:#かなりunder idの時にIndexError
            return None