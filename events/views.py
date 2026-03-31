from django.shortcuts import render, get_object_or_404, redirect
from .models import Event
from guests.models import Guest
import uuid
from django.contrib.auth.decorators import login_required


def event_list(request):
    events = Event.objects.filter(owner=request.user).order_by('-date')
    return render(request, 'events/event_list.html', {'events': events})



def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    pending_event_id = request.session.get('pending_event_id')

    if event.owner:
        if not request.user.is_authenticated or event.owner != request.user:
            return redirect('/login/')
    else:
        if pending_event_id != event.id:
            return redirect('/login/')

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')

        Guest.objects.create(
            event=event,
            full_name=full_name,
            phone=phone,
            email=email,
            token=uuid.uuid4()
        )

        return redirect('event_detail', event_id=event.id)

    guests = Guest.objects.filter(event=event)

    total_guests = guests.count()
    confirmed_guests = guests.filter(status='confirmado').count()
    pending_guests = guests.filter(status='pendente').count()
    declined_guests = guests.filter(status='recusado').count()

    if total_guests > 0:
        percentage = round((confirmed_guests / total_guests) * 100, 1)
    else:
        percentage = 0

    return render(request, 'events/event_detail.html', {
        'event': event,
        'guests': guests,
        'total_guests': total_guests,
        'confirmed_guests': confirmed_guests,
        'pending_guests': pending_guests,
        'declined_guests': declined_guests,
        'percentage': percentage,
    })
    