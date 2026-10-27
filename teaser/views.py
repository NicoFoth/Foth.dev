"""The brain teaser: a first-semester exercise about a small recursive function.

The function on the page is

    def mystery(n):
        if n == 0:
            return 0
        return mystery(n // 2) + n % 2

which counts the 1s in the binary form of n.
"""
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from bits.progress import award, collected

ANSWERS = {'a': 8, 'b': 1023}
BITS = {'a': 'teaser_a', 'b': 'teaser_b'}
FEEDBACK_KEY = 'teaser_feedback'
TRIES_KEY = 'teaser_tries'


def mystery(n):
    """What the function on the page returns, without the recursion."""
    return bin(n).count('1')


def parse(raw):
    """Read 1023, 0x3ff or 0b1111111111. Returns None for anything else."""
    raw = raw.strip().lower()
    for base in (0, 10):  # base 0 understands 0x and 0b but rejects "08"
        try:
            return int(raw, base)
        except ValueError:
            pass
    return None


def hint(task, guess, tries):
    if task == 'a':
        if tries < 2:
            return 'Not quite. Trace a small call by hand first, say mystery(6), and write down what each step adds.'
        return 'Still not it. Write 2025 in binary and compare it with what each step adds.'
    if guess < 0:
        return 'n has to be 0 or more. For a negative n, n // 2 never reaches 0, so mystery never returns.'
    if mystery(guess) == 10:
        return f'mystery({guess}) is 10, but a smaller n gets there too.'
    return f'mystery({guess}) is {mystery(guess)}, not 10.'


def sheet(request):
    have = collected(request)
    return render(request, 'teaser/sheet.html', {
        'solved': {task: BITS[task] in have for task in ANSWERS},
        'answers': ANSWERS,
        'feedback': request.session.pop(FEEDBACK_KEY, None),
    })


@require_POST
def check(request):
    task = request.POST.get('task')
    if task not in ANSWERS:
        return redirect('teaser:sheet')
    raw = request.POST.get('answer', '')[:80]
    guess = parse(raw)
    if guess == ANSWERS[task]:
        award(request, BITS[task])
    else:
        if guess is None:
            text = f'"{raw.strip()}" isn\'t a whole number.'
        else:
            tries = request.session.get(TRIES_KEY, {})
            tries[task] = tries.get(task, 0) + 1
            request.session[TRIES_KEY] = tries
            text = hint(task, guess, tries[task])
        request.session[FEEDBACK_KEY] = {'task': task, 'text': text, 'value': raw.strip()}
    return redirect(reverse('teaser:sheet') + f'#task-{task}')
