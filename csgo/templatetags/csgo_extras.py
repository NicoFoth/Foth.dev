from django import template
from django.templatetags.static import static
from django.utils.html import format_html

register = template.Library()

# (minimum elo, badge) from best to worst. First and last place get their own.
BADGES = [
    (1626, 'omega'), (1576, 'alpha'), (1526, 'beta'),
    (1451, 'gamma'), (1351, 'beep_boop'), (1201, 'bots'),
]


@register.simple_tag
def rank_badge(elo, first=False, last=False):
    if first:
        name = 'niko'
    elif last:
        name = 'schublade'
    else:
        name = next((badge for floor, badge in BADGES if elo >= floor), None)
        if name is None:
            return ''
    return format_html('<img class="rank-badge" src="{}" alt="{}" title="{}">', static(f'csgo/{name}.png'), name, name)
