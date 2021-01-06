from django.shortcuts import render
from django.views import generic
from .models import Article
from .extensions import D2V


class IndexView(generic.ListView):
    template_name = "articles/index.html"
    context_object_name = "pick_up_articles"

    def get_queryset(self):
        return Article.objects.all()


class DetailView(generic.DetailView):
    model = Article
    template_name = 'articles/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        similar_articles_id = D2V().find_similer_articles(self.kwargs['pk'])
        similar_articles = Article.objects.in_bulk(similar_articles_id)
        context['similar_articles'] = similar_articles
        return context

    def get_queryset(self):
        return Article.objects.all()
