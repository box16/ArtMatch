from collections import defaultdict
from gensim import corpora
import os

from db_access import DBAccess
from nlp import NLP

class MyCorpus():
    def __init__(self):
        self.nlp = NLP()
        self.db_access = DBAccess()
        self.pages_num = self.db_access.count_articles()

    def __iter__(self):
        for index in range(self.pages_num):
            body = self.db_access.slect_article_pick_one_body(index)
            yield self.nlp.extract_legal_nouns_verbs(body)

if __name__ == "__main__":
    corpus = MyCorpus()
    dictionary = corpora.Dictionary(corpus)
    once_ids = [tokenid for tokenid, frequency in dictionary.dfs.items() if frequency == 1]
    dictionary.filter_tokens(once_ids)
    dictionary.compactify()

    path = os.environ.get("CORPUSDIR")
    dictionary.save(path+"dictionary.dict")
    
    vector = [dictionary.doc2bow(tokens) for tokens in corpus]
    corpora.MmCorpus.serialize(path+"vector.mm", vector)
    