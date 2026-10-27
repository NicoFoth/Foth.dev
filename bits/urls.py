from django.urls import path

from . import views

app_name = 'stars'

urlpatterns = [
    path('stars/', views.index, name='index'),
    path('stars/claim/', views.claim, name='claim'),
    path('nothing-to-see-here/', views.nothing_to_see_here, name='nothing'),
    path('coffee/', views.coffee, name='coffee'),
]
