from django.shortcuts import render

def index(request):
    context = {"main_message" : "Hello There"}
    return render(request,"articles/index.html",context)