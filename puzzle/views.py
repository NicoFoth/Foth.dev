import time

from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from stars.progress import award, collected

from . import cold_boot

WAIT_KEY = 'puzzle_wait'
COOLDOWN = 10  # seconds, after a wrong answer


def _solved(request):
    have = collected(request)
    return 'puzzle1' in have, 'puzzle2' in have


def day(request):
    p = cold_boot.params(cold_boot.seed_for(request))
    part1, part2 = _solved(request)
    return render(request, 'puzzle/day.html', {
        'part1': part1,
        'part2': part2,
        'answer1': cold_boot.answer(p, 1) if part1 else None,
        'answer2': cold_boot.answer(p, 2) if part2 else None,
    })


def puzzle_input(request):
    p = cold_boot.params(cold_boot.seed_for(request))
    body = '\n'.join(cold_boot.program(p)) + '\n'
    return HttpResponse(body, content_type='text/plain; charset=utf-8')


@require_POST
def answer(request):
    level = 2 if request.POST.get('level') == '2' else 1
    part1, part2 = _solved(request)
    if level == 2 and not part1:
        return redirect('puzzle:day')
    if (part1, part2)[level - 1]:
        return render(request, 'puzzle/answer.html', {'outcome': 'done'})

    now = time.time()
    wait_until = request.session.get(WAIT_KEY, 0)
    if now < wait_until:
        return render(request, 'puzzle/answer.html', {'outcome': 'wait', 'left': int(wait_until - now) + 1})

    raw = request.POST.get('answer', '').strip()
    try:
        guess = int(raw)
    except ValueError:
        return render(request, 'puzzle/answer.html', {'outcome': 'nan', 'guess': raw[:40]})

    p = cold_boot.params(cold_boot.seed_for(request))
    right = cold_boot.answer(p, level)
    if guess == right:
        award(request, f'puzzle{level}', notify=False)
        return render(request, 'puzzle/answer.html', {'outcome': 'right', 'level': level})

    request.session[WAIT_KEY] = now + COOLDOWN
    return render(request, 'puzzle/answer.html', {
        'outcome': 'wrong',
        'direction': 'high' if guess > right else 'low',
        'cooldown': COOLDOWN,
    })
