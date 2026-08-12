from django.shortcuts import render

def index(request):
    return HttpResponse ('<h1>Hello Word!!</h1>')
