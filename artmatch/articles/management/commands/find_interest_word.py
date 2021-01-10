import itertools
import collections
import math
from gensim import corpora, models
from django.core.management.base import BaseCommand
from articles.extensions import NLP, DBAPI


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        nlp = NLP()
        dbapi = DBAPI()

        positive_id = dbapi.select_id_from_articles_sort_limit_top_twenty(
            positive=True)
        negative_id = dbapi.select_id_from_articles_sort_limit_top_twenty(
            positive=False)

        positive_body = [
            dbapi.select_body_from_articles_where_id(id) for id in positive_id]
        negative_body = [
            dbapi.select_body_from_articles_where_id(id) for id in negative_id]
        del(positive_id)
        del(negative_id)

        positive_words = [nlp.extract_legal_nouns_verbs(
            body) for body in positive_body]
        negative_words = [nlp.extract_legal_nouns_verbs(
            body) for body in negative_body]
        del(positive_body)
        del(negative_body)

        positive_set = self.pick_important_words(positive_words)
        negative_set = self.pick_important_words(negative_words)
        del(positive_words)
        del(negative_words)

        positive_result = positive_set - negative_set
        negative_result = negative_set - positive_set
        del(positive_set)
        del(negative_set)

        for word in positive_result:
            # 今回はpositiveとして取られたが、過去にnegativeとして登録されているものは除外
            if dbapi.check_already_exists_word(word, positive=False):
                continue
            dbapi.insert_word(word, positive=True)

        for word in negative_result:
            # 今回はnegativeとして取られたが、過去にpositiveとして登録されているものは除外
            if dbapi.check_already_exists_word(word, positive=True):
                continue
            dbapi.insert_word(word, positive=False)

    def pick_important_words(self, words):
        dictionary = corpora.Dictionary(words)
        corpus = [dictionary.doc2bow(word) for word in words]
        tfidf = models.TfidfModel(corpus)
        corpus_tfidf = tfidf[corpus]
        result = []
        for doc in corpus_tfidf:
            for word in doc:
                result += [(dictionary[word[0]], word[1])]
        pick_num = math.ceil(len(result) * 0.2)
        result = set([word for word, value in sorted(
            result, key=lambda x:x[1], reverse=True)[:pick_num]])
        return result
