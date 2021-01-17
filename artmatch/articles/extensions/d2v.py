import os
from gensim.models.doc2vec import Doc2Vec
from gensim.models.doc2vec import TaggedDocument
from .nlp import NLP
from .db_api import DBAPI


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
