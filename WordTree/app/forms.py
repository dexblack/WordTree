"""
Definition of forms.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _

class BootstrapAuthenticationForm(AuthenticationForm):
    """Authentication form which uses bootstrap CSS."""
    username = forms.CharField(max_length=254,
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'User name'}))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder':'Password'}))

class AddMenu(forms.Form):
    parent = forms.CharField(label='Parent')
    name = forms.CharField(label='Menu', help_text='Enter the menu name', max_length=50, widget=forms.TextInput(attrs={'autofocus':'autofocus'}))
    next = forms.CharField(widget=forms.HiddenInput())
    #data = forms.CharField(label='Other data', widget=forms.Textarea())

class EditMenu(forms.Form):
    id = forms.IntegerField(label='Id', widget=forms.NumberInput(attrs={'readonly':'readonly'}))
    name = forms.CharField(label='Menu', help_text='Enter the menu name', max_length=50, widget=forms.TextInput(attrs={'autofocus':'autofocus'}))
    next = forms.CharField(widget=forms.HiddenInput())
