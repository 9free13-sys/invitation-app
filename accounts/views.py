import logging
import uuid

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import redirect, render

from .forms import LoginForm, CustomRegisterForm
from .models import UserProfile

logger = logging.getLogger(__name__)


def send_verification_email(request, user, profile):
    profile.email_verification_token = uuid.uuid4()
    profile.email_verified = False
    profile.save()

    site_url = settings.SITE_URL.rstrip('/')
    verification_link = f"{site_url}/verify-email/{profile.email_verification_token}/"

    subject = 'Verifica o teu email no Kixanu'
    body = (
        f"Olá {user.username},\n\n"
        f"Verifica o teu email neste link:\n{verification_link}\n\n"
        f"Se não foste tu, ignora este email.\n"
    )

    logger.info("A tentar enviar email de verificação para: %s", user.email)
    logger.info("Link de verificação: %s", verification_link)

    email = EmailMultiAlternatives(
        subject=subject,
        body=body,
        to=[user.email]
    )
    email.send(fail_silently=False)

    logger.info("Email enviado com sucesso para: %s", user.email)


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = CustomRegisterForm(request.POST)

        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.email = form.cleaned_data['email'].strip().lower()
                user.username = form.cleaned_data['username'].strip().lower()
                user.save()

                profile, _ = UserProfile.objects.get_or_create(user=user)

                send_verification_email(request, user, profile)

                messages.success(request, 'Conta criada. Verifica o teu email.')
                return redirect(f"/resend-verification/?email={user.email}")

            except Exception as e:
                logger.exception("Erro no registo/envio de email: %s", e)
                messages.error(request, 'Erro interno no registo ou no envio do email.')
        else:
            messages.error(request, 'Corrige os erros do formulário.')
    else:
        form = CustomRegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def verify_email(request, token):
    try:
        profile = UserProfile.objects.get(email_verification_token=token)
        profile.email_verified = True
        profile.save()
        messages.success(request, 'Email verificado com sucesso.')
        return redirect('login')

    except UserProfile.DoesNotExist:
        messages.error(request, 'Link inválido.')
        return redirect('login')


def resend_verification_email_view(request):
    email = request.GET.get('email')

    if not email and request.method == 'GET':
        return render(request, 'accounts/resend_verification.html', {'email': ''})

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()

        if not email:
            messages.error(request, 'Introduz um email.')
            return render(request, 'accounts/resend_verification.html', {'email': ''})

        try:
            user = User.objects.get(email__iexact=email)
            profile = UserProfile.objects.get(user=user)

            if profile.email_verified:
                messages.info(request, 'Email já verificado.')
                return redirect('login')

            send_verification_email(request, user, profile)
            messages.success(request, 'Email reenviado.')

        except User.DoesNotExist:
            messages.error(request, 'Email não encontrado.')

        except Exception as e:
            logger.exception("Erro resend: %s", e)
            messages.error(request, 'Erro interno.')

    return render(request, 'accounts/resend_verification.html', {'email': email})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = LoginForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        identifier = form.cleaned_data['identifier'].strip()
        password = form.cleaned_data['password']

        try:
            if '@' in identifier:
                user = User.objects.get(email__iexact=identifier)
            else:
                user = User.objects.get(username__iexact=identifier)
        except User.DoesNotExist:
            form.add_error('identifier', 'Utilizador não existe.')
            return render(request, 'accounts/login.html', {'form': form})

        if not user.check_password(password):
            form.add_error('password', 'Password incorreta.')
            return render(request, 'accounts/login.html', {'form': form})

        profile = UserProfile.objects.get(user=user)

        if not profile.email_verified:
            return redirect(f"/resend-verification/?email={user.email}")

        user.backend = 'accounts.backends.EmailOrUsernameBackend'
        login(request, user)
        return redirect('home')

    return render(request, 'accounts/login.html', {'form': form})


@login_required
def profile_view(request):
    profile = UserProfile.objects.get(user=request.user)

    if request.method == 'POST':
        request.user.email = request.POST.get('email')
        request.user.save()

        profile.phone = request.POST.get('phone')
        profile.save()

        messages.success(request, 'Perfil atualizado.')
        return redirect('profile')

    return render(request, 'accounts/profile.html', {'profile': profile})


@login_required
def change_password_view(request):
    form = PasswordChangeForm(request.user, request.POST or None)

    if request.method == 'POST' and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        messages.success(request, 'Password alterada.')
        return redirect('profile')

    return render(request, 'accounts/change_password.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')