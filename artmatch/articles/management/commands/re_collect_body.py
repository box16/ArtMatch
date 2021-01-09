import re
from django.core.management.base import BaseCommand
from articles.extensions import Crawler,DBAPI

web_sites = [
             {"domain": "https://www.lifehacker.jp/",
              "body_tag": "[id='realEntryBody']",
              },
             {"domain": "https://yuchrszk.blogspot.com/",
              "body_tag": "[class='post-single-body post-body']",
              },
             {"domain": "https://gigazine.net/",
              "body_tag": "[class='cntimage']",
              },
             {"domain": "https://studyhacker.net/",
              "body_tag": "[class='entry-content']",
              },
             ]

class Command(BaseCommand):
    def handle(self,*args,**kwargs):
        crawler = Crawler()
        dbapi = DBAPI()
        total_num = dbapi.count_articles()
        for index in range(total_num):
            print(f"{index}/{total_num}")
            pick_url = dbapi.pick_one_article(index)[2]
            bs_object = crawler.get_bs_object(pick_url)
            print(f"{pick_url}")
            for site in web_sites:
                if site["domain"] in pick_url:
                    body = crawler.extract_element(bs_object,site["body_tag"],is_body=True)
                    break
            if body:
                dbapi.update_body(pick_url,body)
                print(f"update!!")
            else:
                print(f"can't update..")
