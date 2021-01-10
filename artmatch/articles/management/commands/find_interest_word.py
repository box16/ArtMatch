import itertools
import collections
import math
from gensim import corpora,models
from django.core.management.base import BaseCommand
from articles.extensions import NLP,DBAPI

class Command(BaseCommand):
    def handle(self,*args,**kwargs):
        nlp = NLP()
        dbapi = DBAPI()

        top_id = dbapi.select_top_articles_id_sorted_interest_index(positive=True)
        worst_id = dbapi.select_top_articles_id_sorted_interest_index(positive=False)

        top_body = [dbapi.pick_body_select_id(id) for id in top_id]
        worst_body = [dbapi.pick_body_select_id(id) for id in worst_id]

        top_words = [nlp.extract_legal_nouns_verbs(body) for body in top_body]
        worst_words = [nlp.extract_legal_nouns_verbs(body) for body in worst_body]

        top_set = self.pick_important_words(top_words)
        worst_set = self.pick_important_words(worst_words)

        top_result = top_set - worst_set
        worst_result = worst_set - top_set
        print(top_result)
        print("------------------------------")
        print(worst_result)
    
    def pick_important_words(self,words):
        dictionary = corpora.Dictionary(words)
        corpus = [dictionary.doc2bow(word) for word in words]
        tfidf = models.TfidfModel(corpus)
        corpus_tfidf = tfidf[corpus]
        result = []
        for doc in corpus_tfidf:
            for word in doc:
                result += [(dictionary[word[0]],word[1])]
        pick_num = math.ceil(len(result)*0.2)
        result = set([word for word,value in sorted(result,key=lambda x:x[1],reverse=True)[:pick_num]])
        return result