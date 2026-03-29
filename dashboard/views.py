from django.shortcuts import render
from events.models import Event
from guests.models import Guest


def home(request):
    total_events = Event.objects.count()
    total_guests = Guest.objects.count()
    confirmed_guests = Guest.objects.filter(status='confirmado').count()
    unconfirmed_guests = Guest.objects.filter(status='pendente').count() + Guest.objects.filter(status='recusado').count()

    context = {
        'total_events': total_events,
        'total_guests': total_guests,
        'confirmed_guests': confirmed_guests,
        'unconfirmed_guests': unconfirmed_guests,
    }

    return render(request, 'dashboard/home.html', context)