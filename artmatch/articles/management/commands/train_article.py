from django.core.management.base import BaseCommand
from articles.extensions import D2V

class Command(BaseCommand):
    def handle(self,*args,**kwargs):
        d2v = D2V()
        d2v.training()