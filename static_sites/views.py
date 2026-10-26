import time

from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.html import escape, format_html
from django.utils.safestring import mark_safe

from stars.progress import collected, curl_code, seen
from stars.registry import STARS

from . import scene
from .forms import ContactForm

# Rows of the scene that double as menu entries: (row, label, url name or url).
CALENDAR = [
    (4, 'about', 'show_about_page'),
    (5, 'projects', 'show_projects'),
    (6, 'puzzle', 'puzzle_day'),
    (7, 'stars', 'stars_page'),
    (8, 'contact', 'show_contact_page'),
    (9, 'cs', 'cs_overview'),
    (10, 'poker', 'show_poker_page'),
    (11, 'github', 'https://github.com/NicoFoth'),
    (12, 'terminal', '#terminal'),
    (13, 'legal', 'show_legal_page'),
]

SLOTS = {pos: i for i, pos in enumerate(scene.STAR_SLOTS)}

CLI_AGENTS = ('curl/', 'wget/', 'httpie/', 'xh/')


def _href(target):
    return target if target.startswith(('#', 'http')) else reverse(target)


def _marks(request, label, target):
    if label == 'puzzle':
        have = collected(request)
        return ['puzzle1' in have, 'puzzle2' in have]
    if target.startswith(('#', 'http')):
        return []
    return [target in seen(request)]


def show_landing_page(request):
    have = set(collected(request))
    rows = scene.build(lit=[i for i, star in enumerate(STARS) if star.key in have])
    if request.headers.get('User-Agent', '').lower().startswith(CLI_AGENTS):
        return _plain_landing(request, rows)
    links = {row: (label, _href(target), _marks(request, label, target)) for row, label, target in CALENDAR}
    return render(request, 'static_sites/index.html', {'calendar': _calendar_html(rows, links)})


def _calendar_html(rows, links):
    # Built here rather than in the template: the calendar is white-space: pre,
    # so every stray space or newline between tags would show up on screen.
    out = []
    for y, runs in enumerate(rows):
        art, x = '', 0
        for text, m in runs:
            if m == ' ':
                art += escape(text)
            elif m in ('*', 'O'):  # a star slot; site.js lights it up when a star is found
                art += format_html('<span class="sc-{}" data-slot="{}">{}</span>', m, SLOTS[(y, x)], text)
            else:
                art += format_html('<span class="sc-{}{}">{}</span>', m, ' moon' if m == 'm' else '', text)
            x += len(text)
        if y not in links:
            out.append(f'<span>{art}</span>')
            continue
        label, href, marks = links[y]
        stars = ''.join(f'<span class="cal-mark{" on" if on else ""}">*</span>' for on in marks)
        extra = ' data-open-terminal' if href == '#terminal' else ''
        out.append(format_html(
            '<a href="{}"{}>{}  <span class="cal-label">{}</span>{}</a>',
            href, mark_safe(extra), mark_safe(art), f'{label:<9}', mark_safe(stars),
        ))
    return mark_safe(''.join(out))


def _plain_landing(request, rows):
    art = scene.ansi(rows)
    for row, label, target in CALENDAR:
        if target == '#terminal':
            continue
        href = target if target.startswith('http') else request.build_absolute_uri(reverse(target))
        art[row] += f'   \x1b[38;5;34m{label:<9}\x1b[0m \x1b[38;5;240m{href}\x1b[0m'
    text = '\n'.join(art) + f"""

  \x1b[1;38;5;46mFoth.dev\x1b[0m  Nico Foth, software engineer.

  You fetched this with a terminal instead of a browser. Respect.
  The website has a terminal too (press \x1b[1m:\x1b[0m). Type this into it:

      \x1b[38;5;227munlock {curl_code()}\x1b[0m

"""
    return HttpResponse(text, content_type='text/plain; charset=utf-8')


def show_about_page(request):
    return render(request, 'static_sites/about.html')


def show_legal_page(request):
    return render(request, 'static_sites/legal.html')


class AdminLogin(LoginView):
    template_name = 'static_sites/admin_login.html'


def show_contact_page(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            last = request.session.get('contact_sent', 0)
            if form.cleaned_data['website']:
                pass  # a bot; pretend everything went fine
            elif time.time() - last < 60:
                form.add_error(None, 'You just sent a message. Give it a minute.')
                return render(request, 'static_sites/contact.html', {'form': form})
            else:
                form.save()
                request.session['contact_sent'] = time.time()
            messages.success(request, "Message received. I'll get back to you.")
            return redirect('show_contact_page')
    else:
        form = ContactForm()
    return render(request, 'static_sites/contact.html', {'form': form})
