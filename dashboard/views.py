from django.shortcuts import render, redirect
from events.models import Event
from guests.models import Guest
from django.contrib.auth.decorators import login_required
def create_invite(request):
    if request.method == 'POST':
        event = Event.objects.create(
            name=request.POST['event_name'],
            event_type=request.POST['event_type'],
            date=request.POST['event_date'],
            location=request.POST['location']
        )

        return redirect("/")  # por agora

    return render(request, 'create_invite.html', {
        'event_types': Event.EVENT_TYPES
    })
@login_required
def home(request):
    total_events = Event.objects.count()
    total_guests = Guest.objects.count()
    total_confirmed = Guest.objects.filter(status='confirmado').count()
    total_declined = Guest.objects.filter(status='recusado').count()

    return render(request, 'dashboard/home.html', {
        'total_events': total_events,
        'total_guests': total_guests,
        'total_confirmed': total_confirmed,
        'total_declined': total_declined,


        
    })