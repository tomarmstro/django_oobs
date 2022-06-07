from django.urls import path
from . import views
from django_oobs.dash_apps.finished_apps import dash_app

urlpatterns = [
    path('', views.home, name='django_oobs-home'),
    path('about/', views.about, name='django_oobs-about'),
    path('graph/', views.graph, name='django_oobs-graph'),
]
