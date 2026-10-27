from django.test import TestCase
from django.urls import reverse

from .models import CSPlayer


class TeamGeneratorTests(TestCase):
    def setUp(self):
        self.players = [CSPlayer.objects.create(steam_id=str(i), name=f'player{i}') for i in range(4)]

    def test_splits_selected_players_into_two_teams(self):
        response = self.client.post(reverse('cs:select_players'), {'players': [p.pk for p in self.players]})
        self.assertTemplateUsed(response, 'csgo/show_teams.html')
        for player in self.players:
            self.assertContains(response, player.name)

    def test_needs_at_least_four_players(self):
        response = self.client.post(reverse('cs:select_players'), {'players': [p.pk for p in self.players[:2]]})
        self.assertRedirects(response, reverse('cs:select_players'))
