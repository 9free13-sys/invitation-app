from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .forms import CustomAuthenticationForm
from django.contrib.auth import login, logout
from events.models import Event
from .models import UserProfile


def register_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        phone = request.POST.get('phone', '').strip()

        if form.is_valid():
            user = form.save()

            if phone:
                profile, _ = UserProfile.objects.get_or_create(user=user)
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


def logout_view(request):
    logout(request)
    return redirect('/login/')