from django.contrib import messages
from django.db.models import Avg, Case, Count, Sum, When
from django.shortcuts import get_object_or_404, redirect, render

from .forms import SelectPlayers
from .generate_team import generate
from .models import CSMatch, CSPlayer, CSPlayerMatch, CSPlayerSeasonElo, CSSeason

RANKED_AFTER = 10  # matches in a season before a player shows up in its ranking


def cs_overview(request):
    seasons = {}
    for season in CSSeason.objects.order_by('-startDate'):
        seasons[season] = CSPlayerSeasonElo.objects.filter(season=season).select_related('player').order_by('-elo')
    return render(request, "csgo/cs_overview.html", {"seasons": seasons})


def season_overview(request, season_id):
    season_object = get_object_or_404(CSSeason, pk=season_id)
    ranked_ids = (CSPlayerMatch.objects.filter(match__season=season_object)
                  .values('player').annotate(matchCount=Count('match'))
                  .filter(matchCount__gte=RANKED_AFTER).values_list('player', flat=True))
    elos = CSPlayerSeasonElo.objects.filter(season=season_object).select_related('player').order_by('-elo')
    ranked_players = elos.filter(player__pk__in=ranked_ids)
    unranked_players = elos.exclude(player__pk__in=ranked_ids)
    matches = CSMatch.objects.filter(season=season_object).select_related('map', 'mode').order_by("-date")

    return render(request, "csgo/season_overview.html", {
        "season": season_object, "ranked_players": ranked_players,
        "unranked_players": unranked_players, "matches": matches, "ranked_after": RANKED_AFTER,
    })


def match_overview(request, match_id):
    match_object = get_object_or_404(CSMatch.objects.select_related('season', 'map', 'mode'), pk=match_id)
    match_players = CSPlayerMatch.objects.filter(match=match_object).select_related('player').order_by("-kills")
    return render(request, "csgo/match_overview.html", {
        "match": match_object,
        "winners": [p for p in match_players if p.win],
        "losers": [p for p in match_players if not p.win],
    })


STATS = dict(
    kills=Sum('kills'), deaths=Sum('deaths'), assists=Sum('assists'),
    headshots=Sum('headshotKills'), adr=Avg('adr'), enemiesFlashed=Sum('enemiesFlashed'),
    utilityDamage=Sum('utilityDamage'), matchCount=Count('match'),
    winCount=Count(Case(When(win=True, then=1))),
)


def _with_kd(stats):
    stats['kd'] = round(stats['kills'] / stats['deaths'], 2) if stats.get('deaths') else stats.get('kills') or 0
    stats['adr'] = round(stats['adr'] or 0)
    return stats


def player_profile(request, player_id):
    player_object = get_object_or_404(CSPlayer, pk=player_id)
    player_matches = (CSPlayerMatch.objects.filter(player=player_object)
                      .select_related('match__map', 'match__season').order_by("-match__date"))
    season_elos = CSPlayerSeasonElo.objects.filter(player=player_object).select_related('season').order_by("-season__startDate")

    player_stats = _with_kd(player_matches.aggregate(**STATS))
    player_seasons = [
        _with_kd(row) for row in
        CSPlayerMatch.objects.filter(player=player_object)
        .values('match__season', 'match__season__name').annotate(**STATS).order_by('-match__season__startDate')
    ]

    return render(request, "csgo/player_profile.html", {
        "player": player_object, "player_matches": player_matches, "season_elos": season_elos,
        "player_stats": player_stats, "player_seasons": player_seasons,
    })


def select_players(request):
    form = SelectPlayers(request.POST or None)
    if request.method == "POST" and form.is_valid():
        players = form.cleaned_data['players']
        if len(players) >= 4:
            latest = {}
            for row in CSPlayerSeasonElo.objects.filter(player__in=players).order_by('season__startDate'):
                latest[row.player_id] = row.elo
            team_a, team_b = generate({player.name: latest.get(player.pk, 1500) for player in players})
            return render(request, "csgo/show_teams.html", {"team_a": team_a, "team_b": team_b})
        messages.warning(request, "Pick at least four players.")
        return redirect("cs:select_players")
    return render(request, "csgo/select_players.html", {"selectform": form})
