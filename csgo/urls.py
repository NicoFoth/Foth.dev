from django.urls import path

from . import views

urlpatterns=[
    path('', views.show_csgo_stats, name="show_csgo_stats"),
]
