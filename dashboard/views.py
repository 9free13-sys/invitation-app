from django.shortcuts import render
from events.models import Event


def home(request):
    return render(request, 'home.html')


def create_invite(request):
    return render(request, 'create_invite.html', {
        'event_types': Event.EVENT_TYPE_CHOICES
    })