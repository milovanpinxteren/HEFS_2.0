from django import forms
from django.forms import DateInput
from functools import partial
DateInput = partial(forms.DateInput, {'class': 'datepicker'})

class PickbonnenForm(forms.Form):
    begindatum = forms.DateField(widget=DateInput(), required=False)
    einddatum = forms.DateField(widget=DateInput(), required=False)
    conversieID = forms.CharField(required=False)
    routenr = forms.IntegerField(required=False)

class GeneralNumbersForm(forms.Form):
    prognosegetal_diner = forms.IntegerField(required=False)
    prognosegetal_brunch = forms.IntegerField(required=False)
    prognosegetal_gourmet = forms.IntegerField(required=False)
