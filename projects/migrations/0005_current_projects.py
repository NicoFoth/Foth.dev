"""Bring the projects list up to date: Roundup, foth.dev and CS:GO MELON, in that order.

Rows are matched by title, so the migration works on whatever the live database holds.
Meetup became Roundup, Star Survivor goes. Projects this does not know about stay, after
these three.
"""
from django.db import migrations

ROUNDUP = {
    'title': 'Roundup',
    'short_description': 'An app for planning things with friends: invitations, carpools and a chat. It\'s in beta.',
    'description': (
        'A Flutter app for Android and iOS for organising events with friends. It keeps track of '
        'who is invited and who drives whom, and has a chat for everything else. The backend is '
        'Spring Boot on PostgreSQL.\n\n'
        'It started in 2021 as Meetup, on Firebase, and has been rebuilt since. Roundup is in beta '
        'and not in the app stores yet.'
    ),
    'github_link': None,
    'demo_link': None,
    'position': 1,
}

FOTH_DEV = {
    'title': 'foth.dev',
    'short_description': "The site you're reading, built to look like a terminal.",
    'description': (
        'Every page is laid out like a man page, with a tmux bar on top and a shell behind the : key. '
        'Twelve bits are hidden around the site, and the brain teaser sets two of them. '
        'It answers curl, too.\n\n'
        'The server runs Django with SQLite. The browser gets one stylesheet and a little vanilla '
        'JavaScript, and there is no build step.'
    ),
    'github_link': 'https://github.com/NicoFoth/Foth.dev',
    'position': 2,
}

MELON = {
    'title': 'CS:GO MELON',
    'short_description': 'Elo ratings for our Counter-Strike evenings, read straight from the game.',
    'description': (
        'An Elo calculator for Counter-Strike: Global Offensive. It reads a privately hosted match '
        "through Valve's Gamestate Integration and stores the result in an Excel file, or sends it "
        'over a socket to another machine.'
    ),
    'github_link': 'https://github.com/NicoFoth/csgoMELON',
    'position': 3,
}


def put(Project, old_titles, fields):
    """Update the first row whose title matches, or create one."""
    for title in old_titles:
        project = Project.objects.filter(title__iexact=title).order_by('id').first()
        if project:
            for name, value in fields.items():
                setattr(project, name, value)
            project.save()
            return
    Project.objects.create(**fields)


def forwards(apps, schema_editor):
    Project = apps.get_model('projects', 'Project')
    put(Project, ['Roundup', 'Meetup'], ROUNDUP)
    put(Project, ['foth.dev'], FOTH_DEV)
    put(Project, ['CS:GO MELON'], MELON)
    Project.objects.filter(title__iexact='Star Survivor').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0004_project_position'),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
