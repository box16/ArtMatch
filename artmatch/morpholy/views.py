from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic.edit import FormView
from .forms import MorpholyForm

class IndexView(FormView):
    template_name = 'morpholy/index.html'
    form_class = MorpholyForm
    success_url = '/morpholy'