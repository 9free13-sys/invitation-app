from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User


class LoginForm(AuthenticationForm):
    identifier = forms.CharField(
        label='Email ou nome de utilizador',
        widget=forms.TextInput(attrs={
            'placeholder': 'Digite o email ou nome de utilizador'
        })
    )

    password = forms.CharField(
        label='Palavra-passe',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Digite a sua palavra-passe'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'username' in self.fields:
            del self.fields['username']


class CustomRegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label='Email',
        widget=forms.EmailInput(attrs={
            'placeholder': 'Digite o seu email'
        })
    )

    username = forms.CharField(
        required=True,
        label='Nome de utilizador',
        widget=forms.TextInput(attrs={
            'placeholder': 'Escolha um nome de utilizador'
        })
    )

    password1 = forms.CharField(
        label='Palavra-passe',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Crie uma palavra-passe'
        })
    )

    password2 = forms.CharField(
        label='Confirmar palavra-passe',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Repita a palavra-passe'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip().lower()
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Email já existe')
        return email

    def clean_username(self):
        username = (self.cleaned_data.get('username') or '').strip().lower()
        if username and User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('Username já existe')
        return username