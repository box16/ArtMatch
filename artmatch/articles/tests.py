from django.test import TestCase

from django.test import TestCase
from django.urls import reverse

from .models import Articles

def create_article(title="title",url="url",body="body"):
    return Articles.objects.create(title=title,url=url,body=body)

class IndexViewTests(TestCase):
    def test_no_articles(self):
        response = self.client.get(reverse('articles:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No articles are available.")
        self.assertQuerysetEqual(response.context['pick_up_articles'], [])
    
    def test_has_articles(self):
        a = create_article()
        response = self.client.get(reverse('articles:index'))
        self.assertQuerysetEqual(
            response.context['pick_up_articles'],
            ['<Articles: title>']
        )