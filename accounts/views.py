import logging
import uuid

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse
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

    email = EmailMultiAlternatives(
        subject=subject,
        body=body,
        to=[user.email]
    )
    email.send(fail_silently=False)


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
                user.is_active = True
                user.save()

                profile, _ = UserProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'email_verified': False,
                        'email_verification_token': uuid.uuid4()
                    }
                )

                try:
                    send_verification_email(request, user, profile)
                    messages.success(request, 'Conta criada com sucesso. Verifica o teu email.')
                except Exception as email_error:
                    logger.exception('Erro ao enviar email de verificação: %s', email_error)
                    messages.warning(
                        request,
                        'Conta criada com sucesso, mas houve erro ao enviar o email de verificação.'
                    )

                return redirect(f"/resend-verification/?email={user.email}")

            except Exception as register_error:
                logger.exception('Erro no registo: %s', register_error)
                messages.error(
                    request,
                    'Ocorreu um erro interno ao criar a conta. Tenta novamente.'
                )
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
        messages.success(request, 'Email verificado com sucesso. Já podes iniciar sessão.')
        return redirect('login')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Link de verificação inválido ou expirado.')
        return redirect('resend_verification')
    except Exception as verify_error:
        logger.exception('Erro ao verificar email: %s', verify_error)
        messages.error(request, 'Ocorreu um erro ao verificar o email.')
        return redirect('login')


def resend_verification_email_view(request):
    email = request.GET.get('email', '').strip().lower()

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()

        try:
            user = User.objects.get(email__iexact=email)
            profile, _ = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'email_verified': False,
                    'email_verification_token': uuid.uuid4()
                }
            )

            if profile.email_verified:
                messages.info(request, 'Este email já está verificado. Já podes iniciar sessão.')
                return redirect('login')

            try:
                send_verification_email(request, user, profile)
                messages.success(request, 'Enviámos um novo email de verificação.')
            except Exception as email_error:
                logger.exception('Erro ao reenviar email de verificação: %s', email_error)
                messages.error(request, 'Erro ao enviar email de verificação.')

        except User.DoesNotExist:
            messages.error(request, 'Não existe nenhuma conta com este email.')
        except Exception as resend_error:
            logger.exception('Erro ao reenviar verificação: %s', resend_error)
            messages.error(request, 'Ocorreu um erro interno.')

    return render(request, 'accounts/resend_verification.html', {'email': email})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = LoginForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        identifier = form.cleaned_data['identifier'].strip()
        password = form.cleaned_data['password']

        if '@' in identifier:
            try:
                user = User.objects.get(email__iexact=identifier)
            except User.DoesNotExist:
                form.add_error('identifier', 'Este email não existe.')
                return render(request, 'accounts/login.html', {'form': form})
        else:
            try:
                user = User.objects.get(username__iexact=identifier)
            except User.DoesNotExist:
                form.add_error('identifier', 'Este nome de utilizador não existe.')
                return render(request, 'accounts/login.html', {'form': form})

        if not user.check_password(password):
            form.add_error('password', 'Palavra-passe incorreta.')
            return render(request, 'accounts/login.html', {'form': form})

        try:
            profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            messages.error(request, 'Conta inválida. Contacta o suporte.')
            return redirect('login')
        except Exception as login_error:
            logger.exception('Erro no login: %s', login_error)
            messages.error(request, 'Ocorreu um erro interno no login.')
            return redirect('login')

        if not profile.email_verified:
            messages.error(request, 'Tens de verificar o teu email antes de entrar.')
            return redirect(f"/resend-verification/?email={user.email}")

        user.backend = 'accounts.backends.EmailOrUsernameBackend'
        login(request, user)
        return redirect('home')

    return render(request, 'accounts/login.html', {'form': form})


@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'email_verified': False,
            'email_verification_token': uuid.uuid4()
        }
    )

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        phone = request.POST.get('phone', '').strip()

        if email and User.objects.filter(email__iexact=email).exclude(id=request.user.id).exists():
            messages.error(request, 'Email já usado.')
            return render(request, 'accounts/profile.html', {'profile': profile})

        if phone and UserProfile.objects.filter(phone=phone).exclude(user=request.user).exists():
            messages.error(request, 'Telefone já usado.')
            return render(request, 'accounts/profile.html', {'profile': profile})

        email_changed = request.user.email.lower() != email if request.user.email else bool(email)

        request.user.email = email
        request.user.save()

        profile.phone = phone if phone else None

        if email_changed:
            try:
                send_verification_email(request, request.user, profile)
                messages.success(
                    request,
                    'Perfil atualizado. Como alteraste o email, tens de o verificar novamente.'
                )
                return redirect(f"/resend-verification/?email={request.user.email}")
            except Exception as email_error:
                logger.exception('Erro ao enviar verificação após alterar perfil: %s', email_error)
                messages.warning(
                    request,
                    'Perfil atualizado, mas houve erro ao enviar o email de verificação.'
                )
        else:
            profile.save()
            messages.success(request, 'Perfil atualizado.')

        return redirect('/profile/')

    return render(request, 'accounts/profile.html', {'profile': profile})


@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password alterada.')
            return redirect('/profile/')
        else:
            messages.error(request, 'Erro no formulário.')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'accounts/change_password.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('/login/')