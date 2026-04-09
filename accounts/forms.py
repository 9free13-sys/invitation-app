from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class LoginForm(forms.Form):
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
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower().strip()
            if User.objects.filter(email__iexact=email).exists():
                raise forms.ValidationError('Email já existe')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            username = username.lower().strip()
            if User.objects.filter(username__iexact=username).exists():
                raise forms.ValidationError('Nome de utilizador já existe')
        return username