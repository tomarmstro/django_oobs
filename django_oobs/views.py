from django.shortcuts import render
from django.http import HttpResponse


posts = [
    {
        'author': 'Tom A',
        'title': 'Ocean Observer Update 1',
        'content': 'Django website functional. Restructuring Dash app to be more inline with new layout.',
        'date_posted': '1st June, 2022'
    },
    {
        'author': 'Tom A',
        'title': 'Ocean Observer Update 2',
        'content': 'Pending',
        'date_posted': 'X June, 2022'
    }

]

def home(request):
    context = {
        'posts': posts
    }
    return render(request, 'django_oobs/home.html', context)

def about(request):
    return render(request, 'django_oobs/about.html', {'title': 'About'})

def graph(request):
    return render(request, 'django_oobs/graph.html', {'title': 'Graph'})