import itertools
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
        del(top_id)
        del(worst_id)

        top_words = [nlp.extract_legal_nouns_verbs(body) for body in top_body]
        worst_words = [nlp.extract_legal_nouns_verbs(body) for body in worst_body]
        del(top_body)
        del(worst_body)

        top_words = set(itertools.chain.from_iterable(top_words))
        worst_words = set(itertools.chain.from_iterable(worst_words))

        result_top_words = top_words - worst_words
        result_worst_words = worst_words - top_words
        print()
        print(result_top_words)
        print()
        print(result_worst_words)

