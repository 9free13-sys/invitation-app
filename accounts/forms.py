from django import forms
from django.contrib.auth.forms import AuthenticationForm


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label='Nome de utilizador, email ou telefone',
        widget=forms.TextInput(attrs={
            'placeholder': 'Digite o nome de utilizador, email ou telefone'
        })
    )

    password = forms.CharField(
        label='Palavra-passe',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Digite a sua palavra-passe'
        })
    )