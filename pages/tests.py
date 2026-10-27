import re

from django.conf import settings
from django.test import TestCase, override_settings
from django.urls import resolve, reverse

from bits.progress import curl_code
from bits.registry import MENU_PAGES

from .models import ContactMessage


class PageTests(TestCase):
    def test_every_menu_page_renders_and_counts_as_seen(self):
        for name in sorted(MENU_PAGES):
            with self.subTest(name):
                self.assertEqual(self.client.get(reverse(name)).status_code, 200)
        self.assertEqual(set(self.client.session['seen']), MENU_PAGES)

    def test_curl_gets_the_landing_page_as_text(self):
        response = self.client.get('/', HTTP_USER_AGENT='curl/8.5.0')
        self.assertEqual(response['Content-Type'].split(';')[0], 'text/plain')
        self.assertContains(response, curl_code())

    def test_robots_and_humans(self):
        self.assertContains(self.client.get(reverse('pages:robots')), 'Disallow: /admin/')
        self.assertContains(self.client.get(reverse('pages:humans')), 'Nico Foth')
        self.assertIn('humans', self.client.session['bits'])

    def test_paths_hardcoded_in_site_js_exist(self):
        js = (settings.BASE_DIR / 'static/js/site.js').read_text()
        paths = set(re.findall(r"'(/(?:[a-z-]+/)?)'", js))
        self.assertIn('/about/', paths)
        for path in paths:
            resolve(path)

    @override_settings(DEBUG=False)
    def test_404_awards_a_star(self):
        response = self.client.get('/definitely/not/here/')
        self.assertContains(response, 'Off The Map', status_code=404)
        self.assertIn('lost', self.client.session['bits'])


class ContactTests(TestCase):
    message = {'name': 'Ada', 'email': 'ada@example.com', 'subject': 'Hi', 'message': 'Nice site.'}

    def post(self, **extra):
        return self.client.post(reverse('pages:contact'), {**self.message, **extra}, follow=True)

    def test_message_is_saved_once_per_minute(self):
        self.assertContains(self.post(), 'Message received')
        self.assertContains(self.post(), 'Give it a minute')
        self.assertEqual(ContactMessage.objects.count(), 1)

    def test_honeypot_drops_the_message_quietly(self):
        self.assertContains(self.post(website='http://spam.example'), 'Message received')
        self.assertEqual(ContactMessage.objects.count(), 0)
