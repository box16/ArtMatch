import requests
import re
import random
from bs4 import BeautifulSoup

class Crawler:
    def __init__(self):
        pass

    def get_bs_object(self, url):
        try:
            req = requests.get(url)
        except requests.exceptions.RequestException:
            return None
        return BeautifulSoup(req.text, "html.parser")

    def _collect_urls(self, bs_object, link_collector):
        if not bs_object:
            return []
        result_urls = []
        for link in bs_object.find_all("a", href=link_collector):
            if not link.attrs["href"]:
                continue
            result_urls.append(link.attrs["href"])
        return list(set(result_urls))

    def extract_element(self, bs_object, title_selector, body_selector):
        if not bs_object:
            return None
        
        try:
            title = bs_object.select(title_selector)[0].get_text()
            body = bs_object.select(body_selector)[0]
        except IndexError:
            return None
        
        try:
            image = bs_object.select(body_selector+ " img")[0].attrs["src"]
        except IndexError:
            return {"title":title,
                "body" :body,
                "image" :"",
            }

        return {"title":title,
                "body" :body,
                "image" :image,
               }

    def _format_urls(self, urls):
        for index, url in enumerate(urls):
            urls[index] = re.sub(r"/$", "", url)
        return list(set(urls))

    def crawl_urls(self, domain, link_collector, times=20):
        base_url = domain
        progress = 0
        urls = []
        if (times <= 0) or (times >= 100):
            times = 2
        while progress < times:
            bs_object = self.get_bs_object(base_url)
            if not bs_object:
                break
            urls = urls + self._collect_urls(bs_object, link_collector)
            urls = self._format_urls(urls)
            base_url = random.choice(urls)
            progress += 1
        return urls
