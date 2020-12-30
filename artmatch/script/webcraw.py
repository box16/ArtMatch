import requests
from bs4 import BeautifulSoup
import re
import random

class Crawler:
    def __init__(self):
        pass

    def get_bs_object(self, url):
        try:
            req = requests.get(url)
        except requests.exceptions.RequestException:
            return None
        return BeautifulSoup(req.text, "html.parser")
    
    def collect_urls(self,bs_object,link_collector):
        if not bs_object:
            return []
        result_urls = []
        for link in bs_object.find_all("a", href=link_collector):
            if not link.attrs["href"]:
                continue
            result_urls.append(link.attrs["href"])
        return list(set(result_urls))

    def extract_element(self, bs_object, css_selector):
        if not bs_object:
            return ""
        selected_elems = bs_object.select(css_selector)
        if (selected_elems is not None) and (len(selected_elems) > 0):
            return '\n'.join([elem.get_text() for elem in selected_elems])
        else:
            return ""
    
    def format_urls(self,urls):
        for index,url in enumerate(urls):
            urls[index] = re.sub(r"/$", "", url)
        return list(set(urls))
    
    def crawl_urls(self,domein,link_collector,times=20):
        base_url = domein
        progress = 0
        urls = []
        if (times <= 0) or (times >= 100):
            times = 2
        while progress < times:
            bs_object = self.get_bs_object(base_url)
            if not bs_object:
                break
            urls = urls + self.collect_urls(bs_object,link_collector)
            urls = self.format_urls(urls)
            base_url = random.choice(urls)
            progress += 1
        return urls