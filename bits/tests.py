import json

from django.test import TestCase
from django.urls import reverse

from .progress import curl_code


class ClaimTests(TestCase):
    def claim(self, **payload):
        return self.client.post(reverse('stars:claim'), json.dumps(payload), content_type='application/json')

    def stars(self):
        return self.client.session.get('stars', [])

    def test_client_claimable_star(self):
        response = self.claim(key='konami')
        self.assertEqual(response.json()['new'], True)
        self.assertEqual(self.claim(key='konami').json()['new'], False)
        self.assertEqual(self.stars(), ['konami'])

    def test_server_side_stars_cannot_be_claimed(self):
        for key in ('puzzle1', 'puzzle2', 'teapot', 'lost', 'nope'):
            self.assertEqual(self.claim(key=key).status_code, 400)
        self.assertEqual(self.stars(), [])

    def test_curl_code(self):
        self.assertEqual(self.claim(key='curl', code='deadbeef').status_code, 400)
        self.assertEqual(self.claim(key='curl', code=curl_code().upper()).json()['new'], True)


class TeapotTests(TestCase):
    def test_teapot(self):
        self.assertEqual(self.client.get(reverse('stars:coffee')).status_code, 418)
        self.assertIn('teapot', self.client.session['stars'])
