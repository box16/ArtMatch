import unittest
from ..webcraw import Crawler
import re

class TestWebcraw(unittest.TestCase):
    def setUp(self):
        self.crawler = Crawler()
        self.website = {"name": "PaleolithicMan",
                        "domain": "https://yuchrszk.blogspot.com/",
                        "title_tag": "[class='post-title single-title emfont']",
                        "body_tag": "[class='post-single-body post-body']",
                        "link_collector": re.compile("^(?=https://yuchrszk.blogspot.com/..../.+?)(?!.*archive)(?!.*label).*$"),
                        "link_creater": lambda domestic_url: domestic_url,
                        }

    def test_get_page_normal_url(self):
        bs = self.crawler.get_page(self.website["domain"])
        self.assertIsNotNone(bs)
    
    def test_get_page_abnormal_url(self):
        bs = self.crawler.get_page("")
        self.assertIsNone(bs)

    def test_collect_urls_normal_url(self):
        urls = self.crawler.collect_urls(self.website["domain"],
                                       self.website["link_collector"])
        self.assertGreater(len(urls), 0)

    def test_collect_urls_abnormal_url(self):
        urls = self.crawler.collect_urls("",
                                       self.website["link_collector"])
        self.assertEqual(len(urls), 0)

if __name__ == "__main__":
    unittest.main()