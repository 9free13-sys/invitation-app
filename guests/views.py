from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Guest
from events.models import Event


def create_invite(request):
    if request.method == 'POST':
        event = Event.objects.create(
            name=request.POST['event_name'],
            date=request.POST['event_date']
        )

        guest = Guest.objects.create(
            full_name=request.POST['guest_name'],
            phone=request.POST['phone'],
            event=event
        )

        return redirect(f"/invite/{guest.token}/")

    return render(request, 'create_invite.html')


@login_required
def guest_list(request):
    guests = Guest.objects.filter(event__owner=request.user).order_by('-id')
    return render(request, 'guests/guest_list.html', {'guests': guests})


def confirm_guest(request, token):
    guest = get_object_or_404(Guest, token=token)
    guest.status = 'confirmado'
    guest.save()
    return redirect('event_detail', event_id=guest.event.id)


def decline_guest(request, token):
    guest = get_object_or_404(Guest, token=token)
    guest.status = 'recusado'
    guest.save()
    return redirect('event_detail', event_id=guest.event.id)


def invite_page(request, token):
    guest = get_object_or_404(Guest, token=token)
    return render(request, 'guests/public_invite.html', {'guest': guest})


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


def delete_guest(request, guest_id):
    guest = get_object_or_404(Guest, id=guest_id)
    event = guest.event

    if not request.user.is_authenticated:
        messages.error(request, "Precisas de iniciar sessão para eliminar convidados.")
        return redirect('login')

    if event.owner != request.user:
        messages.error(request, "Não tens permissão para eliminar este convidado.")
        return redirect('event_detail', event_id=event.id)

    guest.delete()
    messages.success(request, "Convidado eliminado com sucesso!")
    return redirect('event_detail', event_id=event.id)