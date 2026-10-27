import time

from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from bits.progress import award

from . import landing
from .context_processors import versions
from .forms import ContactForm

CLI_AGENTS = ('curl/', 'wget/', 'httpie/', 'xh/')

CONTACT_COOLDOWN = 60  # seconds between two messages from the same visitor


def _text(body):
    return HttpResponse(body, content_type='text/plain; charset=utf-8')


def home(request):
    if request.headers.get('User-Agent', '').lower().startswith(CLI_AGENTS):
        return _text(landing.text(request))
    return render(request, 'pages/home.html', landing.context(request))


def about(request):
    return render(request, 'pages/about.html')


def legal(request):
    return render(request, 'pages/legal.html')


class Login(LoginView):
    template_name = 'pages/login.html'


def contact(request):
    form = ContactForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        if form.cleaned_data['website']:
            pass  # a bot filled in the honeypot; pretend everything went fine
        elif time.time() - request.session.get('contact_sent', 0) < CONTACT_COOLDOWN:
            form.add_error(None, 'You just sent a message. Give it a minute.')
            return render(request, 'pages/contact.html', {'form': form})
        else:
            form.save()
            request.session['contact_sent'] = time.time()
        messages.success(request, "Message received. I'll get back to you.")
        return redirect('pages:contact')
    return render(request, 'pages/contact.html', {'form': form})


def robots_txt(request):
    return _text('\n'.join([
        'User-agent: *',
        f"Disallow: {reverse('admin:index')}",
        f"Disallow: {reverse('pages:login')}",
        f"Disallow: {reverse('bits:nothing')}",
        '',
    ]))


def humans_txt(request):
    award(request, 'humans', notify=False)
    v = versions()
    return _text(f"""/* TEAM */
    Developer: Nico Foth
    Site: https://foth.dev
    GitHub: https://github.com/NicoFoth

/* SITE */
    Standards: HTML, CSS, a little vanilla JS
    Components: Django {v['django']}, Python {v['python']}, SQLite {v['sqlite']}
    Fonts: B612, made for Airbus cockpit displays, and IBM Plex Mono (both self-hosted)
    Build step: none

    Reading this set one of the hidden bits. Check {request.build_absolute_uri(reverse('bits:index'))}
""")


def not_found(request, exception=None):
    award(request, 'lost')
    return render(request, 'pages/404.html', status=404)
