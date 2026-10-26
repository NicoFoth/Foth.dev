from django.urls import path

from . import views

urlpatterns = [
    path('stars/', views.stars_page, name='stars_page'),
    path('stars/claim/', views.claim, name='stars_claim'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('humans.txt', views.humans_txt, name='humans_txt'),
    path('nothing-to-see-here/', views.nothing_to_see_here, name='nothing_to_see_here'),
    path('coffee/', views.coffee, name='coffee'),
]
