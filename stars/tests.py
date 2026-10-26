import json

from django.test import TestCase, override_settings
from django.urls import reverse

from .progress import curl_code


class ClaimTests(TestCase):
    def claim(self, **payload):
        return self.client.post(reverse('stars_claim'), json.dumps(payload), content_type='application/json')

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


class EasterEggTests(TestCase):
    def test_curl_landing_page_prints_code(self):
        response = self.client.get('/', HTTP_USER_AGENT='curl/8.5.0')
        self.assertEqual(response['Content-Type'].split(';')[0], 'text/plain')
        self.assertContains(response, curl_code())

    def test_teapot(self):
        self.assertEqual(self.client.get(reverse('coffee')).status_code, 418)
        self.assertIn('teapot', self.client.session['stars'])

    @override_settings(DEBUG=False)
    def test_404_awards_a_star(self):
        response = self.client.get('/definitely/not/here/')
        self.assertContains(response, 'Off The Map', status_code=404)
        self.assertIn('lost', self.client.session['stars'])
