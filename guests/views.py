from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files import File
from .models import Guest
from events.models import Event
from invitations.models import Invitation
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
            phone=request.POST.get('phone'),
            email=request.POST.get('email'),
            event=event
        )

        Invitation.objects.get_or_create(
            event=event,
            guest=guest
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


def invite_page(request, slug):
    guest = get_object_or_404(Guest, slug=slug)
    return render(request, 'guests/public_invite.html', {'guest': guest})


def invite_page_by_token(request, token):
    guest = get_object_or_404(Guest, token=token)

    if guest.slug:
        return redirect('invite_page', slug=guest.slug)

    return render(request, 'guests/public_invite.html', {'guest': guest})


def invite_status(request, slug):
    guest = get_object_or_404(Guest, slug=slug)
    return render(request, 'guests/invite_response.html', {
        'guest': guest,
        'action': guest.status
    })


def invite_response(request, slug, action):
    guest = get_object_or_404(Guest, slug=slug)

    invitation, _ = Invitation.objects.get_or_create(
        event=guest.event,
        guest=guest
    )

    if action == 'confirm':
        guest.status = 'confirmado'
        invitation.status = 'accepted'

        if guest.event.allowed_companions > 0:
            companion_name = request.POST.get('companion_name')
            if companion_name:
                guest.companion_name = companion_name

        guest.save()
        invitation.save()

        if not guest.qr_code:
            generate_qr_for_guest(guest)

        guest.refresh_from_db()

    elif action == 'decline':
        guest.status = 'recusado'
        invitation.status = 'declined'
        guest.save()
        invitation.save()

    return render(request, 'guests/invite_response.html', {
        'guest': guest,
        'action': action
    })


def invite_response_by_token(request, token, action):
    guest = get_object_or_404(Guest, token=token)

    if guest.slug:
        return redirect('invite_response', slug=guest.slug, action=action)

    invitation, _ = Invitation.objects.get_or_create(
        event=guest.event,
        guest=guest
    )

    if action == 'confirm':
        guest.status = 'confirmado'
        invitation.status = 'accepted'

        if guest.event.allowed_companions > 0:
            companion_name = request.POST.get('companion_name')
            if companion_name:
                guest.companion_name = companion_name

        guest.save()
        invitation.save()

        if not guest.qr_code:
            generate_qr_for_guest(guest)

        guest.refresh_from_db()

    elif action == 'decline':
        guest.status = 'recusado'
        invitation.status = 'declined'
        guest.save()
        invitation.save()

    return render(request, 'guests/invite_response.html', {
        'guest': guest,
        'action': action
    })


def confirm_guest(request, token):
    guest = get_object_or_404(Guest, token=token)

    invitation, _ = Invitation.objects.get_or_create(
        event=guest.event,
        guest=guest
    )

    guest.status = 'confirmado'
    invitation.status = 'accepted'

    guest.save()
    invitation.save()

    if not guest.qr_code:
        generate_qr_for_guest(guest)

    return render(request, 'guests/invite_response.html', {
        'guest': guest,
        'action': 'confirm'
    })


def decline_guest(request, token):
    guest = get_object_or_404(Guest, token=token)

    invitation, _ = Invitation.objects.get_or_create(
        event=guest.event,
        guest=guest
    )

    guest.status = 'recusado'
    invitation.status = 'declined'

    guest.save()
    invitation.save()

    return render(request, 'guests/invite_response.html', {
        'guest': guest,
        'action': 'decline'
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