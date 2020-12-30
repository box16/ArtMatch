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
        bs_object = self.crawler.get_page(self.website["domain"])
        self.assertIsNotNone(bs_object)

    def test_get_page_abnormal_url(self):
        bs_object = self.crawler.get_page("")
        self.assertIsNone(bs_object)

    def test_collect_urls_normal_url(self):
        bs_object = self.crawler.get_page(self.website["domain"])
        urls = self.crawler.collect_urls(bs_object,
                                         self.website["link_collector"])
        self.assertGreater(len(urls), 0)

    def test_collect_urls_abnormal_url(self):
        bs_object = self.crawler.get_page("")
        urls = self.crawler.collect_urls(bs_object,
                                         self.website["link_collector"])
        self.assertEqual(len(urls), 0)

    def test_safe_get_normal_url_title(self):
        bs_object = self.crawler.get_page("https://yuchrszk.blogspot.com/2020/12/20208.html")
        elems = self.crawler.safe_get(bs_object,
                                     self.website["title_tag"])
        self.assertGreater(len(elems), 0)

    def test_safe_get_abnormal_url_title(self):
        bs_object = self.crawler.get_page("")
        elems = self.crawler.safe_get(bs_object,
                                     self.website["title_tag"])
        self.assertEqual(len(elems), 0)
    
    def test_safe_get_normal_url_body(self):
        bs_object = self.crawler.get_page("https://yuchrszk.blogspot.com/2020/12/20208.html")
        elems = self.crawler.safe_get(bs_object,
                                        self.website["body_tag"])
        self.assertGreater(len(elems), 0)

    def test_safe_get_abnormal_url_body(self):
        bs_object = self.crawler.get_page("")
        elems = self.crawler.safe_get(bs_object,
                                     self.website["body_tag"])
        self.assertEqual(len(elems), 0)

if __name__ == "__main__":
    unittest.main()