from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views import generic
from django.urls import reverse
from .models import Article, Interest
from .extensions import D2V


class IndexView(generic.ListView):
    template_name = "articles/index.html"
    context_object_name = "pick_up_articles"

    def get_queryset(self):
        return Article.objects.all()[:100]


class DetailView(generic.DetailView):
    model = Article
    template_name = 'articles/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        similar_articles_id = find_similer_articles(self.kwargs['pk'])
        similar_articles = Article.objects.in_bulk(similar_articles_id)
        context['similar_articles'] = similar_articles
        return context

    def get_queryset(self):
        return Article.objects.all()


def find_similer_articles(base_id, id_only=True):
    similer_article = D2V().find_similer_articles(base_id)
    if id_only:
        return [id for id, similality in similer_article]
    else:
        return similer_article


def vote(request, article_id):
    try:
        base_interest = get_object_or_404(Interest, article_id=article_id)
        add_score = 1 if (request.POST["preference"] == "like") else -1
        update_list = [(base_interest, add_score)]

        similer_article = find_similer_articles(article_id, id_only=False)
        similer_interest = [
            (get_object_or_404(
                Interest,
                article_id=id),
                add_score *
                similality) for id,
            similality in similer_article]

        update_list = update_list + similer_interest
        for interest, score in update_list:
            interest.interest_index += score
            interest.save()
        return HttpResponseRedirect(
            reverse(
                'articles:detail', args=(
                    article_id,)))

    except(KeyError, Interest.DoesNotExist):
        return render(
            request,
            'articles/detail.html',
            {
                'article': Article.objects.get(
                    pk=article_id),
                'error_message': "好みが選択されずに登録ボタンが押されました",
                'similar_articles': Article.objects.in_bulk(
                    find_similer_articles(article_id))})
