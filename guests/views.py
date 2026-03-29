from django.shortcuts import redirect, get_object_or_404, render
from .models import Guest


def guest_list(request):
    guests = Guest.objects.all().order_by('-id')
    return render(request, 'guests/guest_list.html', {'guests': guests})


def confirm_guest(request, guest_id):
    guest = get_object_or_404(Guest, id=guest_id)
    guest.confirmed = True
    guest.save()
    return redirect('event_detail', event_id=guest.event.id)


def decline_guest(request, guest_id):
    guest = get_object_or_404(Guest, id=guest_id)
    guest.confirmed = False
    guest.save()
    return redirect('event_detail', event_id=guest.event.id)

def invite_page(request, token):
    guest = get_object_or_404(Guest, token=token)
    return render(request, 'guests/invite_page.html', {'guest': guest})

def invite_response(request, token, action):
    guest = get_object_or_404(Guest, token=token)

    if action == 'confirm':
        guest.status = 'confirmado'
    elif action == 'decline':
        guest.status = 'recusado'

    guest.save()

    return render(request, 'guests/invite_response.html', {
        'guest': guest,
        'action': action
    })