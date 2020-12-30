from webcraw import Crawler
from db_access import DBAccess
import re

web_sites = [{"name": "LifeHacker",
              "domain": "https://www.lifehacker.jp/",
              "title_tag": "[class='lh-entryDetail-header'] h1",
              "body_tag": "[id='realEntryBody'] p",
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
              "body_tag": "[class='preface']",
              "link_collector": re.compile("^(https://gigazine.net/news/20)"),
              "link_creater": lambda domestic_url: domestic_url,
              },
             ]

if __name__ == "__main__":
    crawler = Crawler()
    db_accesser = DBAccess()
    for site in web_sites:
        urls = crawler.crawl_urls(site["domain"],
                                  site["link_collector"],times=1)
        
        for index,url in enumerate(urls):
            urls[index] = site["link_creater"](url)
        
        for url in urls:
            bs_object = crawler.get_bs_object(url)
            title = crawler.extract_element(bs_object,site["title_tag"])
            body = crawler.extract_element(bs_object,site["body_tag"])
            db_accesser.insert_article(title=title,url=url,body=body)




