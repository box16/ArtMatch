import unittest
from ..webcraw import Crawler

class TestWebcraw(unittest.TestCase):
    def setUp(self):
        self.crawler = Crawler()

    def test_get_page_normal_url(self):
        bs = self.crawler.get_page("https://docs.python.org/ja/3/library/unittest.html")
        self.assertIsNotNone(bs)
    
    def test_get_page_abnormal_url(self):
        bs = self.crawler.get_page("")
        self.assertIsNone(bs)

if __name__ == "__main__":
    unittest.main()