from django.urls import path

from . import views

app_name = 'teaser'

urlpatterns = [
    path('', views.sheet, name='sheet'),
    path('check/', views.check, name='check'),
]
