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
    
    def collect_urls(self,bs_object,link_collector):
        if not bs_object:
            return []
        result_urls = []
        for link in bs_object.find_all("a", href=link_collector):
            if not link.attrs["href"]:
                continue
            result_urls.append(link.attrs["href"])
        return list(set(result_urls))

    def safe_get(self, bs_object, css_selector):
        if not bs_object:
            return []
        selected_elems = bs_object.select(css_selector)
        if (selected_elems is not None) and (len(selected_elems) > 0):
            return '\n'.join([elem.get_text() for elem in selected_elems])
        else:
            return []