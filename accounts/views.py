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


def send_verification_email(request, user, profile, force_new_token=False):
    if force_new_token or not profile.email_verification_token:
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

    email = EmailMultiAlternatives(
        subject=subject,
        body=body,
        to=[user.email]
    )
    email.send(fail_silently=False)


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = CustomRegisterForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            try:
                email = form.cleaned_data['email'].strip().lower()
                username = form.cleaned_data['username'].strip().lower()

                user = form.save(commit=False)
                user.email = email
                user.username = username
                user.save()

                profile, _ = UserProfile.objects.get_or_create(user=user)

                try:
                    send_verification_email(request, user, profile, force_new_token=False)
                    messages.success(request, 'Conta criada. Verifica o teu email.')
                except Exception as email_error:
                    logger.exception("Erro ao enviar email de verificação no registo: %s", email_error)
                    messages.warning(
                        request,
                        'Conta criada, mas não foi possível enviar o email de verificação agora.'
                    )

                return redirect(f"/resend-verification/?email={user.email}")

            except Exception as e:
                logger.exception("Erro no registo: %s", e)
                messages.error(request, 'Erro interno no registo.')
        else:
            messages.error(request, 'Corrige os erros do formulário.')

    return render(request, 'accounts/register.html', {'form': form})


def verify_email(request, token):
    try:
        profile = UserProfile.objects.get(email_verification_token=token)

        if profile.email_verified:
            messages.info(request, 'Este email já foi verificado.')
            return redirect('login')

        profile.email_verified = True
        profile.save()

        messages.success(request, 'Email verificado com sucesso.')
        return redirect('login')

    except UserProfile.DoesNotExist:
        messages.error(request, 'Link inválido.')
        return redirect('login')

    except Exception as e:
        logger.exception("Erro ao verificar email: %s", e)
        messages.error(request, 'Erro interno ao verificar email.')
        return redirect('login')


def resend_verification_email_view(request):
    email = (request.GET.get('email') or '').strip().lower()

    if request.method == 'POST':
        email = (request.POST.get('email') or '').strip().lower()

        if not email:
            messages.error(request, 'Introduz um email válido.')
            return render(request, 'accounts/resend_verification.html', {'email': ''})

        try:
            user = User.objects.get(email__iexact=email)
            profile, _ = UserProfile.objects.get_or_create(user=user)

            if profile.email_verified:
                messages.info(request, 'Este email já está verificado.')
                return redirect('login')

            send_verification_email(request, user, profile, force_new_token=False)
            messages.success(request, 'Email de verificação reenviado com sucesso.')

        except User.DoesNotExist:
            messages.error(request, 'Não existe nenhuma conta com este email.')
        except Exception as e:
            logger.exception("Erro ao reenviar email de verificação: %s", e)
            messages.error(request, 'Não foi possível reenviar o email de verificação neste momento.')

        return render(request, 'accounts/resend_verification.html', {'email': email})

    return render(request, 'accounts/resend_verification.html', {'email': email})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = LoginForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        identifier = form.cleaned_data['identifier'].strip().lower()
        password = form.cleaned_data['password']

        try:
            if '@' in identifier:
                user = User.objects.get(email__iexact=identifier)
            else:
                user = User.objects.get(username__iexact=identifier)
        except User.DoesNotExist:
            form.add_error('identifier', 'Utilizador não existe.')
            return render(request, 'accounts/login.html', {'form': form})
        except Exception as e:
            logger.exception("Erro ao procurar utilizador no login: %s", e)
            messages.error(request, 'Erro interno no login.')
            return render(request, 'accounts/login.html', {'form': form})

        if not user.check_password(password):
            form.add_error('password', 'Password incorreta.')
            return render(request, 'accounts/login.html', {'form': form})

        try:
            profile, _ = UserProfile.objects.get_or_create(user=user)
        except Exception as e:
            logger.exception("Erro ao obter perfil no login: %s", e)
            messages.error(request, 'Erro interno no login.')
            return render(request, 'accounts/login.html', {'form': form})

        if not profile.email_verified:
            return redirect(f"/resend-verification/?email={user.email}")

        user.backend = 'accounts.backends.EmailOrUsernameBackend'
        login(request, user)
        return redirect('home')

    return render(request, 'accounts/login.html', {'form': form})


@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        try:
            new_email = (request.POST.get('email') or '').strip().lower()
            new_phone = request.POST.get('phone')

            email_changed = request.user.email != new_email

            request.user.email = new_email
            request.user.save()

            profile.phone = new_phone

            if email_changed and new_email:
                profile.email_verified = False
                if not profile.email_verification_token:
                    profile.email_verification_token = uuid.uuid4()

            profile.save()

            if email_changed and new_email:
                try:
                    send_verification_email(request, request.user, profile, force_new_token=False)
                    messages.success(
                        request,
                        'Perfil atualizado. Verifica o novo email para continuares a usá-lo.'
                    )
                except Exception as email_error:
                    logger.exception("Erro ao reenviar verificação após alterar email: %s", email_error)
                    messages.warning(
                        request,
                        'Perfil atualizado, mas houve um erro ao enviar o novo email de verificação.'
                    )
            else:
                messages.success(request, 'Perfil atualizado.')

            return redirect('profile')

        except Exception as e:
            logger.exception("Erro ao atualizar perfil: %s", e)
            messages.error(request, 'Erro ao atualizar perfil.')

    return render(request, 'accounts/profile.html', {'profile': profile})


@login_required
def change_password_view(request):
    form = PasswordChangeForm(request.user, request.POST or None)

    if request.method == 'POST' and form.is_valid():
        try:
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password alterada.')
            return redirect('profile')
        except Exception as e:
            logger.exception("Erro ao alterar password: %s", e)
            messages.error(request, 'Erro ao alterar password.')

    return render(request, 'accounts/change_password.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')