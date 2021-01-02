from collections import defaultdict
from pprint import pprint
from db_access import DBAccess
from nlp import NLP

if __name__ == "__main__":
    db_access = DBAccess()
    nlp = NLP()

    # 分かち書き
    bodys = db_access.slect_article_pick_body()
    corpus = []
    for body in bodys:
        corpus.append(nlp.extract_legal_nouns_verbs(body[0]))
    
    # 一度しか出現しない単語の削除
    frequency = defaultdict(int)
    for document in corpus:
        for token in document:
            frequency[token] += 1
    corpus = [
        [token for token in document if frequency[token] > 1]
        for document in corpus
    ]
