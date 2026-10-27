from django.urls import path

from . import views

app_name = 'puzzle'

urlpatterns = [
    path('', views.day, name='day'),
    path('input', views.puzzle_input, name='input'),
    path('answer', views.answer, name='answer'),
]
