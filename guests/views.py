from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files import File
from .models import Guest
from events.models import Event
import qrcode
import tempfile


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

        return redirect(f"/invite/{guest.slug}/")

    return render(request, 'create_invite.html')


@login_required
def guest_list(request):
    guests = Guest.objects.filter(event__owner=request.user).order_by('-id')
    return render(request, 'guests/guest_list.html', {'guests': guests})


def generate_qr_for_guest(guest):
    qr_data = f"Kixanu|event:{guest.event.id}|guest:{guest.id}|token:{guest.token}|status:{guest.status}"

    qr = qrcode.make(qr_data)

    with tempfile.NamedTemporaryFile(suffix='.png') as temp_file:
        qr.save(temp_file, format='PNG')
        temp_file.seek(0)
        guest.qr_code.save(f'guest_{guest.id}_qr.png', File(temp_file), save=True)


def confirm_guest(request, token):
    guest = get_object_or_404(Guest, token=token)
    guest.status = 'confirmado'
    guest.save()

    if not guest.qr_code:
        generate_qr_for_guest(guest)

    return render(request, 'guests/invite_response.html', {
        'guest': guest,
        'action': 'confirm'
    })


def decline_guest(request, token):
    guest = get_object_or_404(Guest, token=token)
    guest.status = 'recusado'
    guest.save()

    return render(request, 'guests/invite_response.html', {
        'guest': guest,
        'action': 'decline'
    })


def invite_page(request, slug):
    guest = get_object_or_404(Guest, slug=slug)
    return render(request, 'guests/public_invite.html', {'guest': guest})


def invite_response(request, slug, action):
    guest = get_object_or_404(Guest, slug=slug)

    if action == 'confirm':
        guest.status = 'confirmado'

        if guest.event.allowed_companions > 0:
            companion_name = request.POST.get('companion_name')
            if companion_name:
                guest.companion_name = companion_name

        guest.save()

        if not guest.qr_code:
            generate_qr_for_guest(guest)

        guest.refresh_from_db()

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