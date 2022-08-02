from django.urls import path
from . import views
from django_oobs.dash_apps.finished_apps import dash_app
from django_oobs.dash_apps.finished_apps import map_app
# from django_oobs.dash_apps.finished_apps import temperature_app

urlpatterns = [
    path('', views.about, name='django_oobs-about'),
    # path('temperature/', views.temperature, name='django_oobs-temperature'),
    path('data/', views.data, name='django_oobs-data'),
]
