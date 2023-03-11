from django.forms.widgets import SelectDateWidget
from django import forms
from django.utils import timezone


class DateRangeForm(forms.Form):
    YEARS = range(2017, timezone.now().year + 2)

    start_date = forms.DateField(label='Startdatum', widget=SelectDateWidget(years=YEARS))
    end_date = forms.DateField(label='Enddatum', widget=SelectDateWidget(years=YEARS))


class CompareForm(forms.Form):
    compare = forms.IntegerField(label='Vergleich mit Vorjahren', initial=0)
    normalize = forms.BooleanField(label='Normalisieren', required=False)
