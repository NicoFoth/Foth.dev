from django import forms

from .models import CSPlayer


class SelectPlayers(forms.Form):
    players = forms.ModelMultipleChoiceField(
        queryset=CSPlayer.objects.order_by('name'),
        widget=forms.CheckboxSelectMultiple,
        label='Spieler',
    )
