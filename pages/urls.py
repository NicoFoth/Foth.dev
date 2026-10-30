from django.urls import path

from . import views

app_name = 'pages'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('legal/', views.legal, name='legal'),
    path('admin-login/', views.Login.as_view(), name='login'),
    path('robots.txt', views.robots_txt, name='robots'),
    path('humans.txt', views.humans_txt, name='humans'),
]
