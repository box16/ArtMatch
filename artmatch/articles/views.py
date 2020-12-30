from django.shortcuts import render
from django.views import generic
from .models import Articles

class IndexView(generic.ListView):
    template_name = "articles/index.html"
    context_object_name = "pick_up_articles"

    def get_queryset(self):
        return Articles.objects.all()


class DetailView(generic.DetailView):
    model = Articles
    template_name = 'articles/detail.html'

    def get_queryset(self):
         return Articles.objects.all()