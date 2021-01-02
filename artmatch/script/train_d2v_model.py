from db_access import DBAccess
from nlp import NLP

if __name__ == "__main__":
    db_access = DBAccess()
    nlp = NLP()

    bodys = db_access.slect_article_pick_body()
    corpus = []
    for body in bodys:
        corpus.append(nlp.extract_legal_nouns_verbs(body[0]))
    print(corpus[1:4])