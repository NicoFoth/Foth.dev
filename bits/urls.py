from django.urls import path

from . import views

app_name = 'bits'

urlpatterns = [
    path('bits/', views.index, name='index'),
    path('bits/claim/', views.claim, name='claim'),
    path('nothing-to-see-here/', views.nothing_to_see_here, name='nothing'),
    path('coffee/', views.coffee, name='coffee'),
]
