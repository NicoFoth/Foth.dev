import json

from django.test import TestCase
from django.urls import reverse

from .progress import curl_code


class ClaimTests(TestCase):
    def claim(self, **payload):
        return self.client.post(reverse('bits:claim'), json.dumps(payload), content_type='application/json')

    def bits(self):
        return self.client.session.get('bits', [])

    def test_client_claimable_bit(self):
        response = self.claim(key='konami')
        self.assertEqual(response.json()['new'], True)
        self.assertEqual(self.claim(key='konami').json()['new'], False)
        self.assertEqual(self.bits(), ['konami'])

    def test_server_side_bits_cannot_be_claimed(self):
        for key in ('teaser_a', 'teaser_b', 'teapot', 'lost', 'moon', 'nope'):
            self.assertEqual(self.claim(key=key).status_code, 400)
        self.assertEqual(self.bits(), [])

    def test_curl_code(self):
        self.assertEqual(self.claim(key='curl', code='deadbeef').status_code, 400)
        self.assertEqual(self.claim(key='curl', code=curl_code().upper()).json()['new'], True)


class TeapotTests(TestCase):
    def test_teapot(self):
        self.assertEqual(self.client.get(reverse('bits:coffee')).status_code, 418)
        self.assertIn('teapot', self.client.session['bits'])
