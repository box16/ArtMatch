import numpy
from django.core.management.base import BaseCommand
from articles.extensions.db_api import DBAPI


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        dbapi = DBAPI()

        positive_words = dbapi.select_word(positive=True)
        negative_words = dbapi.select_word(positive=False)

        positive_words_num = len(positive_words)
        negative_words_num = len(negative_words)

        id_hits_score_set = {}
        total_num = dbapi.count_articles()
        for index in range(total_num):
            print(f"{index}/{total_num}")
            article = dbapi.select_articles_offset_limit_one(index)

            positive_hits = 0
            for word in positive_words:
                if word in article[1]:
                    positive_hits += 1

            negative_hits = 0
            for word in negative_words:
                if word in article[1]:
                    negative_hits += 1

            hits_score = (positive_hits / positive_words_num) + \
                (1 - (negative_hits / negative_words_num))
            id_hits_score_set[article[0]] = hits_score

        del(positive_words)
        del(negative_words)

        hits_score_average = numpy.average(
            [float(value) for value in id_hits_score_set.values()])
        hits_score_std = numpy.std([float(value)
                                    for value in id_hits_score_set.values()])

        counter = 0
        for _id, hits_score in id_hits_score_set.items():
            print(f"{counter}/{total_num}")
            score = int(
                ((hits_score - hits_score_average) / hits_score_std) * 10) + 50
            dbapi.update_score_where_article_id(_id, score)
            counter += 1
