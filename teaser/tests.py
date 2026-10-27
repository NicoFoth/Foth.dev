from django.test import TestCase
from django.urls import reverse

from . import views


def mystery(n):
    """The function exactly as the page shows it."""
    if n == 0:
        return 0
    return mystery(n // 2) + n % 2


class TeaserMathTests(TestCase):
    def test_shortcut_matches_the_function_on_the_page(self):
        for n in range(5000):
            self.assertEqual(views.mystery(n), mystery(n))

    def test_answers(self):
        self.assertEqual(views.ANSWERS['a'], mystery(2025))
        self.assertEqual(views.ANSWERS['b'], next(n for n in range(5000) if mystery(n) == 10))

    def test_parse_reads_decimal_hex_and_binary(self):
        for raw in ['1023', ' 1023 ', '0x3FF', '0b1111111111', '1_023']:
            self.assertEqual(views.parse(raw), 1023, raw)
        self.assertEqual(views.parse('08'), 8)
        for raw in ['', 'ten', '1.5', '0x']:
            self.assertIsNone(views.parse(raw), raw)


class TeaserViewTests(TestCase):
    def check(self, task, answer):
        return self.client.post(reverse('teaser:check'), {'task': task, 'answer': answer}, follow=True)

    def bits(self):
        return self.client.session.get('stars', [])

    def test_parts_can_be_solved_in_any_order(self):
        self.assertNotContains(self.check('b', '0x3ff'), 'Both parts solved')
        self.assertEqual(self.bits(), ['teaser_b'])
        self.assertContains(self.check('a', '8'), 'Both parts solved')
        self.assertEqual(self.bits(), ['teaser_b', 'teaser_a'])

    def test_wrong_answers_get_tutor_feedback_and_no_cooldown(self):
        self.assertContains(self.check('b', '1000'), 'mystery(1000) is 6, not 10.')
        self.assertContains(self.check('b', '1535'), 'a smaller n gets there too')
        self.assertContains(self.check('a', '11'), 'Trace a small call by hand')
        self.assertContains(self.check('a', '12'), 'Write 2025 in binary')
        self.assertEqual(self.bits(), [])
        self.check('b', '1023')
        self.assertEqual(self.bits(), ['teaser_b'])

    def test_not_a_number(self):
        response = self.check('a', 'eight')
        self.assertContains(response, 'a whole number')
        self.assertContains(response, 'value="eight"')

    def test_unknown_task_is_ignored(self):
        self.assertRedirects(self.client.post(reverse('teaser:check'), {'task': 'c', 'answer': '1'}), reverse('teaser:sheet'))
