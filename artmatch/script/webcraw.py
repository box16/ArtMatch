import requests
from bs4 import BeautifulSoup

class Crawler:
    def __init__(self):
        pass

    def get_page(self, url):
        try:
            req = requests.get(url)
        except requests.exceptions.RequestException:
            return None
        return BeautifulSoup(req.text, "html.parser")
    
    def collect_urls(self,base_url,link_collector):
        bs = self.get_page(base_url)
        if not bs:
            return []
        result_urls = []
        for link in bs.find_all("a", href=link_collector):
            if not link.attrs["href"]:
                continue
            result_urls.append(link.attrs["href"])
        return list(set(result_urls))