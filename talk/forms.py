from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django import forms
from django.contrib.auth import get_user_model
from talk.models import Message
import autocomplete_light


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        widgets = {
            'body': forms.Textarea(attrs={ 'rows': 3 }),
        }


class ThreadForm(forms.Form):
    recipients = forms.CharField(
        widget=autocomplete_light.TextWidget(
            'UserAutocomplete', attrs={
                'placeholder': _('Search for recipients, separate by comma...'),
                'minimum_characters': 3,
        })
    )
    body = forms.CharField(
        widget=forms.Textarea(
            attrs={ 'rows': 3 }
        )
    )
