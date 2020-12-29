from django.db import models

class Articles(models.Model):
    title = models.TextField()
    url = models.TextField()
    body = models.TextField()

    def __str__(self):
        return f"{self.title}"