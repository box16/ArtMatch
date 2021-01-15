import unittest
from articles.extensions import NLP

class TestNLP(unittest.TestCase):
    def setUp(self):
        self.nlp = NLP()

    def test_extract_legal_nouns_verbs_check_nouns(self):
        document = "今日はとても良い天気です"
        result = self.nlp.extract_legal_nouns_verbs(document)

        self.assertIn("今日", result)
        self.assertIn("天気", result)
        self.assertNotIn("は", result)
        self.assertNotIn("とても", result)
        self.assertNotIn("良い", result)
        self.assertNotIn("です", result)

    def test_extract_legal_nouns_verbs_check_verbs(self):
        document = "野球はボールを打って捕って走るスポーツです"
        result = self.nlp.extract_legal_nouns_verbs(document)

        self.assertIn("打つ", result)
        self.assertIn("捕る", result)
        self.assertIn("走る", result)
        self.assertNotIn("て", result)
        self.assertNotIn("は", result)
        self.assertNotIn("を", result)
        self.assertNotIn("です", result)

    def test_extract_legal_nouns_verbs_check_unknown(self):
        """現時点では「マウスウォッシュ」が認識されなかった"""
        document = "マウスウォッシュがヤバい"
        result = self.nlp.extract_legal_nouns_verbs(document)

        self.assertNotIn("マウスウォッシュ", result)