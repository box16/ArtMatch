import os
from gensim import corpora
from gensim import models
from gensim import similarities
from collections import defaultdict
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

    vector = [dictionary.doc2bow(tokens) for tokens in corpus]
    
    tfidf = models.TfidfModel(vector)
    corpus_tfidf = tfidf[vector]

    lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=300)
    corpus_lsi = lsi[corpus_tfidf]

    path = os.environ.get("CORPUSDIR")
    index = similarities.Similarity(path+"sim.index",corpus_lsi,300)

    dictionary.save(path+"dictionary.dict")
    corpora.MmCorpus.serialize(path+"vector.mm", vector)
    tfidf.save(path+"model.tfidf")
    lsi.save(path+"model.lsi")
    index.save(path+"index.index")

