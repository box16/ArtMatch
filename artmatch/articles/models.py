from django.db import models


class Article(models.Model):
    title = models.TextField()
    url = models.TextField()
    body = models.TextField()

    def __str__(self):
        return f"{self.title}"


class Interest(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    interest_index = models.FloatField(default=0)

    def __str__(self):
        return f"{self.article.title}"


class InterestWord(models.Model):
    word = models.TextField(unique=True)

    def __str__(self):
        return f"{self.word}"


class NotInterestWord(models.Model):
    word = models.TextField(unique=True)

    def __str__(self):
        return f"{self.word}"
