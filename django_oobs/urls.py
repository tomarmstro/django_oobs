from django.urls import path
from . import views
from django_oobs.dash_apps.finished_apps import dash_app
from django_oobs.dash_apps.finished_apps import map_app
# from django_oobs.dash_apps.finished_apps import temperature_app

urlpatterns = [
    path('about/', views.about, name='django_oobs-about'),
    path('', views.home, name='django_oobs-home'),
    path('data/', views.data, name='django_oobs-data'),
]
