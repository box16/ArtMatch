from django.shortcuts import render
from django.views import generic
from .models import Articles

class IndexView(generic.ListView):
    template_name = "articles/index.html"
    context_object_name = "pick_up_articles"

    def get_queryset(self):
        """とりあえず、頭5個をピックアップとしている"""
        return Articles.objects.all()[:5]