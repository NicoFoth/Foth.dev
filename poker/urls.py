from django.urls import path

from . import views

app_name = 'poker'

urlpatterns = [
    path('', views.index, name='index'),
]
