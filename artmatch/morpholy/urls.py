from django.urls import path

from . import views

app_name = "morpholy"
urlpatterns = [
    path('', views.index, name='index'),
]