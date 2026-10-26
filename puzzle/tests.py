import time
from unittest import mock

from django.test import TestCase
from django.urls import reverse

from . import cold_boot
from .cold_boot import Params


class ColdBootMathTests(TestCase):
    def test_closed_form_matches_interpreter(self):
        for p in [Params(1, 1, 1, 1), Params(5, 3, 7, 10), Params(12, 9, 4, 99), Params(30, 4, 21, 42)]:
            lines = cold_boot.program(p)
            self.assertEqual(cold_boot.run(lines), cold_boot.answer(p, 1))
            self.assertEqual(cold_boot.run(lines, c=1), cold_boot.answer(p, 2))

    def test_params_are_deterministic_and_in_range(self):
        for seed in range(50):
            p = cold_boot.params(seed)
            self.assertEqual(p, cold_boot.params(seed))
            self.assertTrue(250 <= p.n <= 400 and 3 <= p.k <= 9)
            self.assertTrue(900 <= p.x <= 1400 and 10 <= p.m <= 99)


class ColdBootViewTests(TestCase):
    def seed(self):
        self.client.get(reverse('puzzle_day'))
        return cold_boot.params(self.client.session[cold_boot.SESSION_KEY])

    def test_input_is_plain_text_and_stable(self):
        first = self.client.get(reverse('puzzle_input'))
        self.assertEqual(first['Content-Type'], 'text/plain; charset=utf-8')
        self.assertEqual(first.content, self.client.get(reverse('puzzle_input')).content)

    def test_wrong_then_right(self):
        p = self.seed()
        right = cold_boot.answer(p, 1)
        resp = self.client.post(reverse('puzzle_answer'), {'level': 1, 'answer': right + 1})
        self.assertContains(resp, 'too high')
        resp = self.client.post(reverse('puzzle_answer'), {'level': 1, 'answer': right})
        self.assertContains(resp, 'wait')  # cooldown after a wrong answer

        later = time.time() + 60
        with mock.patch('puzzle.views.time.time', return_value=later):
            resp = self.client.post(reverse('puzzle_answer'), {'level': 1, 'answer': right})
        self.assertContains(resp, 'the right answer')
        self.assertIn('puzzle1', self.client.session['stars'])

    def test_part_two_locked_until_part_one(self):
        p = self.seed()
        resp = self.client.post(reverse('puzzle_answer'), {'level': 2, 'answer': cold_boot.answer(p, 2)})
        self.assertNotIn('puzzle2', self.client.session.get('stars', []))
        self.assertEqual(resp.status_code, 302)
