from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic.edit import FormView
from .forms import MorpholyForm

posted_data = {"text" : "",
               "select_part" : []}

class IndexView(FormView):
    template_name = 'morpholy/index.html'
    form_class = MorpholyForm
    success_url = 'result'

    def form_valid(self,form):
        posted_data["text"] = form.data.get("text")
        posted_data["select_part"] = form.data.getlist("select_part")
        return super().form_valid(form)

def result_view(request):
    return render(request,'morpholy/result.html',posted_data)