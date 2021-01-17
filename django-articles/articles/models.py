from django.db import models


class Article(models.Model):
    title = models.TextField()
    url = models.TextField()
    body = models.TextField()
    image = models.URLField(max_length=250, default="")

    def __str__(self):
        return f"{self.title}"


class Interest(models.Model):
    article = models.OneToOneField(Article, on_delete=models.CASCADE)
    interest_index = models.FloatField(default=0)

    def __str__(self):
        return f"{self.article.title} : {self.interest_index}"


class PositiveWord(models.Model):
    word = models.TextField(unique=True)

    def __str__(self):
        return f"{self.word}"


class NegativeWord(models.Model):
    word = models.TextField(unique=True)

    def __str__(self):
        return f"{self.word}"


class Score(models.Model):
    article = models.OneToOneField(Article, on_delete=models.CASCADE)
    score = models.IntegerField(default=50)

    def __str__(self):
        return f"{self.article.title} : {self.score}"
