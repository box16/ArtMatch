import os
from gensim import corpora
from gensim import models
import logging

if __name__ == "__main__":
    
    path = os.environ.get("CORPUSDIR")
    corpus = corpora.MmCorpus(path+"vector.mm")
    dictionary = corpora.Dictionary.load(path+"dictionary.dict")
    
    tfidf = models.TfidfModel(corpus)
    corpus_tfidf = tfidf[corpus]

    lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=10)
    corpus_lsi = lsi[corpus_tfidf]

    tfidf.save(path+"model.tfidf")
    lsi.save(path+"lsi.tfidf")