import re
from django.core.management.base import BaseCommand
from articles.extensions.webcraw import Crawler
from articles.extensions.db_api import DBAPI

web_sites = [{"name": "LifeHacker",
              "domain": "https://www.lifehacker.jp/",
              "title_tag": "[class='lh-entryDetail-header'] h1",
              "body_tag": "[id='realEntryBody']",
              "link_collector": re.compile("^(/20)"),
              "link_creater": lambda domestic_url: "https://www.lifehacker.jp/" + domestic_url,
              },
             {"name": "PaleolithicMan",
              "domain": "https://yuchrszk.blogspot.com/",
              "title_tag": "[class='post-title single-title emfont']",
              "body_tag": "[class='post-single-body post-body']",
              "link_collector": re.compile("^(?=https://yuchrszk.blogspot.com/..../.+?)(?!.*archive)(?!.*label).*$"),
              "link_creater": lambda domestic_url: domestic_url,
              },
             {"name": "Gigazine",
              "domain": "https://gigazine.net/",
              "title_tag": "[class='cntimage'] h1",
              "body_tag": "[class='cntimage']",
              "link_collector": re.compile("^(https://gigazine.net/news/20)"),
              "link_creater": lambda domestic_url: domestic_url,
              },
             {"name": "StudyHacker",
              "domain": "https://studyhacker.net/",
              "title_tag": "[class='entry-title']",
              "body_tag": "[class='entry-content']",
              "link_collector": re.compile("^(https://studyhacker.net/)(?!.*archive/)"),
              "link_creater": lambda domestic_url: domestic_url,
              },
             ]


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        crawler = Crawler()
        dbapi = DBAPI()
        for site in web_sites:
            urls = crawler.crawl_urls(site["domain"],
                                      site["link_collector"],
                                      times=20)

            for index, url in enumerate(urls):
                urls[index] = site["link_creater"](url)

            for url in urls:
                bs_object = crawler.get_bs_object(url)
                elements = crawler.extract_element(bs_object, site["title_tag"],site["body_tag"])
                if elements:
                    dbapi.insert_article(title=elements["title"], url=url, body=elements["body"],image=elements["image"])
