from django.urls import path

from . import views

urlpatterns = [
    path('', views.day, name='puzzle_day'),
    path('input', views.puzzle_input, name='puzzle_input'),
    path('answer', views.answer, name='puzzle_answer'),
]
