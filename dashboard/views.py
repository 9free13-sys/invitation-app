from django.shortcuts import render, redirect
from events.models import Event
from guests.models import Guest
from django.contrib.auth.decorators import login_required
def create_invite(request):
    if request.method == 'POST':
        event = Event.objects.create(
    owner=request.user,
    name=request.POST['event_name'],
    event_type=request.POST['event_type'],
    date=request.POST['event_date'],
    location=request.POST['location'],
    description=request.POST.get('description', '')

)

        return redirect('event_detail', event_id=event.id)  # por agora

    return render(request, 'create_invite.html', {
        'event_types': Event.EVENT_TYPES
    })
@login_required
def home(request):
    user_events = Event.objects.filter(owner=request.user)
    total_events = user_events.count()
    total_guests = Guest.objects.filter(event__owner=request.user).count()
    total_confirmed = Guest.objects.filter(event__owner=request.user, status='confirmado').count()
    total_declined = Guest.objects.filter(event__owner=request.user, status='recusado').count()

    
    return render(request, 'dashboard/home.html', {
        'total_events': total_events,
        'total_guests': total_guests,
        'total_confirmed': total_confirmed,
        'total_declined': total_declined,


        
    })