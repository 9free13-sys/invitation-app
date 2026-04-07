from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from .forms import CustomAuthenticationForm
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from events.models import Event
from .models import UserProfile


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()

        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, 'Este nome de utilizador já existe.')
            return render(request, 'accounts/register.html', {
                'form': form,
                'phone': phone,
                'email': email,
            })

        if email and User.objects.filter(email__iexact=email).exists():
            messages.error(request, 'Este email já está registado.')
            return render(request, 'accounts/register.html', {
                'form': form,
                'phone': phone,
                'email': email,
            })

        if phone and UserProfile.objects.filter(phone=phone).exists():
            messages.error(request, 'Este telefone já está em uso.')
            return render(request, 'accounts/register.html', {
                'form': form,
                'phone': phone,
                'email': email,
            })

        if form.is_valid():
            user = form.save(commit=False)
            user.email = email
            user.save()

            profile, _ = UserProfile.objects.get_or_create(user=user)
            if phone:
                profile.phone = phone
                profile.save()

            login(request, user)

            pending_event_id = request.session.get('pending_event_id')
            if pending_event_id:
                try:
                    event = Event.objects.get(id=pending_event_id, owner__isnull=True)
                    event.owner = user
                    event.save()
                    del request.session['pending_event_id']
                    return redirect('event_detail', event_id=event.id)
                except Event.DoesNotExist:
                    pass

            return redirect('/')

        messages.error(request, 'Corrige os erros do formulário e tenta novamente.')

    else:
        form = UserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            pending_event_id = request.session.get('pending_event_id')
            if pending_event_id:
                try:
                    event = Event.objects.get(id=pending_event_id)
                    if event.owner is None:
                        event.owner = user
                        event.save()
                    del request.session['pending_event_id']
                    return redirect('event_detail', event_id=event.id)
                except Event.DoesNotExist:
                    pass

            return redirect('/')
    else:
        form = CustomAuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()

        if email and User.objects.filter(email__iexact=email).exclude(id=request.user.id).exists():
            messages.error(request, 'Este email já está registado por outro utilizador.')
            return render(request, 'accounts/profile.html', {
                'profile': profile
            })

        if phone and UserProfile.objects.filter(phone=phone).exclude(user=request.user).exists():
            messages.error(request, 'Este telefone já está em uso por outro utilizador.')
            return render(request, 'accounts/profile.html', {
                'profile': profile
            })

        request.user.email = email
        request.user.save()

        profile.phone = phone if phone else None
        profile.save()

        messages.success(request, 'Perfil atualizado com sucesso.')
        return redirect('/profile/?updated=1')

    return render(request, 'accounts/profile.html', {
        'profile': profile
    })


@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Palavra-passe alterada com sucesso.')
            return redirect('/profile/?password_updated=1')
        else:
            messages.error(request, 'Corrige os erros do formulário.')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'accounts/change_password.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('/login/')