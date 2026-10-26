from django.db.models import Sum
from django.shortcuts import render

from .models import PokerPlayer, PokerSeason


def show_poker_page(request):
    seasons = {}
    for season in PokerSeason.objects.order_by('-start_date'):
        seasons[season] = (PokerPlayer.objects
                           .filter(pokerplayergameperformance__game__season=season)
                           .annotate(balance=Sum('pokerplayergameperformance__chips'))
                           .order_by('-balance'))
    return render(request, "poker/show_poker_page.html", {"seasons_data": seasons})
