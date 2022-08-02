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

def about(request):

    return render(request, 'django_oobs/about.html', {'title': 'about'})

# def temperature(request):
#     return render(request, 'django_oobs/temperature.html', {'title': 'temperature'})

def data(request):
    return render(request, 'django_oobs/data.html', {'title': 'data'})