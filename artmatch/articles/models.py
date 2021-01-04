from django.db import models

class Articles(models.Model):
    title = models.TextField()
    url = models.TextField()
    body = models.TextField()

    def __str__(self):
        return f"{self.title}"

class Interests(models.Model):
    article = models.ForeignKey(Articles, on_delete=models.CASCADE)
    interest_index = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.article.title}"