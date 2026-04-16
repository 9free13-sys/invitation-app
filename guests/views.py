from io import BytesIO
import base64
import json
import qrcode

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from events.models import Event
from invitations.models import Invitation
from .models import Guest


def verify_qr(request):
    token = request.GET.get('token')

    try:
        guest = Guest.objects.get(token=token)

        if guest.checked_in:
            return JsonResponse({
                'valid': False,
                'message': 'Já fez check-in'
            })

        guest.checked_in = True
        guest.checked_in_at = timezone.now()
        guest.save()

        return JsonResponse({
            'valid': True,
            'message': f'{guest.full_name} confirmado com sucesso'
        })

    except Guest.DoesNotExist:
        return JsonResponse({
            'valid': False,
            'message': 'QR inválido'
        })

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


def get_qr_code_base64(guest):
    qr_data = (
        f"Kixanu|event:{guest.event.id}|guest:{guest.id}|"
        f"token:{guest.token}|status:{guest.status}"
    )

    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)

    qr_image = qr.make_image(fill_color='black', back_color='white')

    buffer = BytesIO()
    qr_image.save(buffer, format='PNG')
    buffer.seek(0)

    return base64.b64encode(buffer.getvalue()).decode('utf-8')


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

    qr_code_base64 = None
    if guest.status == 'confirmado':
        qr_code_base64 = get_qr_code_base64(guest)

    return render(request, 'guests/invite_response.html', {
        'guest': guest,
        'action': guest.status,
        'qr_code_base64': qr_code_base64,
    })


def invite_response(request, slug, action):
    guest = get_object_or_404(Guest, slug=slug)

    invitation, _ = Invitation.objects.get_or_create(
        event=guest.event,
        guest=guest
    )

    qr_code_base64 = None

    if action == 'confirm':
        guest.status = 'confirmado'
        invitation.status = 'accepted'

        if hasattr(guest.event, 'allowed_companions') and guest.event.allowed_companions > 0:
            companion_name = request.POST.get('companion_name')
            if companion_name:
                guest.companion_name = companion_name

        guest.save()
        invitation.save()
        guest.refresh_from_db()

        qr_code_base64 = get_qr_code_base64(guest)

    elif action == 'decline':
        guest.status = 'recusado'
        invitation.status = 'declined'
        guest.save()
        invitation.save()

    return render(request, 'guests/invite_response.html', {
        'guest': guest,
        'action': action,
        'qr_code_base64': qr_code_base64,
    })


def invite_response_by_token(request, token, action):
    guest = get_object_or_404(Guest, token=token)

    if guest.slug:
        return redirect('invite_response', slug=guest.slug, action=action)

    invitation, _ = Invitation.objects.get_or_create(
        event=guest.event,
        guest=guest
    )

    qr_code_base64 = None

    if action == 'confirm':
        guest.status = 'confirmado'
        invitation.status = 'accepted'

        if hasattr(guest.event, 'allowed_companions') and guest.event.allowed_companions > 0:
            companion_name = request.POST.get('companion_name')
            if companion_name:
                guest.companion_name = companion_name

        guest.save()
        invitation.save()
        guest.refresh_from_db()

        qr_code_base64 = get_qr_code_base64(guest)

    elif action == 'decline':
        guest.status = 'recusado'
        invitation.status = 'declined'
        guest.save()
        invitation.save()

    return render(request, 'guests/invite_response.html', {
        'guest': guest,
        'action': action,
        'qr_code_base64': qr_code_base64,
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
    guest.refresh_from_db()

    qr_code_base64 = get_qr_code_base64(guest)

    return render(request, 'guests/invite_response.html', {
        'guest': guest,
        'action': 'confirm',
        'qr_code_base64': qr_code_base64,
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
        'action': 'decline',
        'qr_code_base64': None,
    })


@login_required
def scan_qr_page(request, event_id):
    event = get_object_or_404(Event, id=event_id, owner=request.user)
    return render(request, 'guests/scan_qr.html', {'event': event})


@login_required
def validate_qr_code(request, event_id):
    if request.method != 'POST':
        return JsonResponse({
            'ok': False,
            'message': 'Método inválido.'
        }, status=405)

    event = get_object_or_404(Event, id=event_id, owner=request.user)

    try:
        payload = json.loads(request.body.decode('utf-8'))
        qr_text = (payload.get('qr_text') or '').strip()
    except Exception:
        return JsonResponse({
            'ok': False,
            'message': 'QR inválido.'
        }, status=400)

    if not qr_text.startswith('Kixanu|'):
        return JsonResponse({
            'ok': False,
            'message': 'Este QR não pertence ao Kixanu.'
        }, status=400)

    parts = qr_text.split('|')
    qr_data = {}

    for part in parts[1:]:
        if ':' in part:
            key, value = part.split(':', 1)
            qr_data[key] = value

    try:
        qr_event_id = int(qr_data.get('event', '0'))
        qr_guest_id = int(qr_data.get('guest', '0'))
        qr_token = qr_data.get('token', '')
    except ValueError:
        return JsonResponse({
            'ok': False,
            'message': 'Dados do QR inválidos.'
        }, status=400)

    if qr_event_id != event.id:
        return JsonResponse({
            'ok': False,
            'message': 'Este QR pertence a outro evento.'
        }, status=400)

    guest = get_object_or_404(
        Guest,
        id=qr_guest_id,
        event_id=qr_event_id,
        token=qr_token
    )

    if guest.status != 'confirmado':
        return JsonResponse({
            'ok': False,
            'message': f'O convidado está com estado "{guest.status}".',
            'guest_name': guest.full_name,
            'status': guest.status,
            'checked_in': guest.checked_in,
        }, status=400)

    if guest.checked_in:
        return JsonResponse({
            'ok': True,
            'message': 'Este convidado já teve entrada registada.',
            'guest_name': guest.full_name,
            'status': guest.status,
            'checked_in': True,
            'checked_in_at': guest.checked_in_at.strftime('%d/%m/%Y %H:%M') if guest.checked_in_at else '',
        })

    guest.checked_in = True
    guest.checked_in_at = timezone.localtime()
    guest.save(update_fields=['checked_in', 'checked_in_at'])

    return JsonResponse({
        'ok': True,
        'message': 'Entrada confirmada com sucesso.',
        'guest_name': guest.full_name,
        'status': guest.status,
        'checked_in': True,
        'checked_in_at': guest.checked_in_at.strftime('%d/%m/%Y %H:%M'),
        'companion_name': guest.companion_name or '',
    })


def delete_guest(request, guest_id):
    guest = get_object_or_404(Guest, id=guest_id)
    event = guest.event

    if not request.user.is_authenticated:
        messages.error(request, 'Precisas de iniciar sessão para eliminar convidados.')
        return redirect('login')

    if event.owner != request.user:
        messages.error(request, 'Não tens permissão para eliminar este convidado.')
        return redirect('event_detail', event_id=event.id)

    guest.delete()
    messages.success(request, 'Convidado eliminado com sucesso!')
    return redirect('event_detail', event_id=event.id)