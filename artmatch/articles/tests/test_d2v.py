import unittest
from articles.extensions.d2v import D2V

class TestD2V(unittest.TestCase):
    def setUp(self):
        self.d2v = D2V()

    def test_find_similer_articles_normal_id(self):
        result = self.d2v.find_similer_articles(1)
        self.assertIsNotNone(result)

    def test_find_similer_articles_over_id(self):
        result = self.d2v.find_similer_articles(999999)
        self.assertIsNone(result)

    def test_find_similer_articles_under_id(self):
        result = self.d2v.find_similer_articles(-999999)
        self.assertIsNone(result)