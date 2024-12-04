from functools import partial

from django import forms
from django.contrib.auth.forms import AuthenticationForm

from hefs.models import HalfproductenIngredienten, ProductenHalfproducts

DateInput = partial(forms.DateInput, {'class': 'datepicker'})


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label='Username/Order-ID',  # Custom label
        widget=forms.TextInput(attrs={'autofocus': True})
    )
    password = forms.CharField(
        label='Password/Postcode',  # Custom label
        widget=forms.PasswordInput
    )

class PickbonnenForm(forms.Form):
    begindatum = forms.DateField(widget=DateInput(), required=False)
    einddatum = forms.DateField(widget=DateInput(), required=False)
    conversieID = forms.CharField(required=False)
    routenr = forms.IntegerField(required=False)


class GeneralNumbersForm(forms.Form):
    prognosegetal_diner = forms.IntegerField(required=False)
    prognosegetal_brunch = forms.IntegerField(required=False)
    prognosegetal_gourmet = forms.IntegerField(required=False)


class HalfproductenIngredientenForm(forms.ModelForm):
    class Meta:
        model = HalfproductenIngredienten
        fields = ['halfproduct', 'ingredient', 'quantity']

        widgets = {
            'halfproduct': forms.TextInput(attrs={'class': 'autocomplete-halfproduct', 'autocomplete': 'off'}),
            'ingredient': forms.TextInput(attrs={'class': 'autocomplete-ingredient', 'autocomplete': 'off'}),
        }

        labels = {
            'quantity': 'Nodig per Eenheid',
        }

class ProductenHalfproductenForm(forms.ModelForm):
    class Meta:
        model = ProductenHalfproducts
        fields = ['product', 'halfproduct', 'quantity']

        widgets = {
            'product': forms.TextInput(attrs={'class': 'autocomplete-product', 'autocomplete': 'off'}),
            'halfproduct': forms.TextInput(attrs={'class': 'autocomplete-halfproduct', 'autocomplete': 'off'}),
        }

        labels = {
            'quantity': 'Nodig per Portie',
        }