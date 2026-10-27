from django import forms

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    # Humans never see this field; bots that fill in everything do.
    website = forms.CharField(required=False, label='Leave this empty')

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {'message': forms.Textarea(attrs={'rows': 8})}
