from django.urls import path

from . import views

app_name = 'cs'

urlpatterns = [
    path('', views.cs_overview, name='index'),
    path('select-players', views.select_players, name='select_players'),
    path('seasons/<str:season_id>', views.season_overview, name='season'),
    path('matches/<str:match_id>', views.match_overview, name='match'),
    path('players/<str:player_id>', views.player_profile, name='player'),
]
