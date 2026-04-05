from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from notifications.models import Notification
from events.models import Event
from guests.models import Guest
from guests.views import generate_qr_for_guest


class Command(BaseCommand):
    help = 'Cria notificações e envia lembretes por email sobre eventos próximos para organizadores e convidados confirmados.'

    def handle(self, *args, **kwargs):
        today = timezone.localdate()

        organizer_reminder_days = [7, 3, 1, 0]
        guest_reminder_days = [60, 30, 15, 7, 3, 1, 0]

        events = Event.objects.exclude(owner__isnull=True)

        created_count = 0
        organizer_email_count = 0
        guest_email_count = 0

        for event in events:
            if not event.date:
                continue

            days_left = (event.date - today).days

            if days_left < 0:
                continue

            owner = event.owner

            # Lembretes do organizador
            if owner and days_left in organizer_reminder_days:
                if days_left == 0:
                    owner_title = f"O evento {event.name} é hoje"
                    owner_message = f"O evento {event.name} acontece hoje. Verifica os convidados e os preparativos finais."
                elif days_left == 1:
                    owner_title = f"Falta 1 dia para o evento {event.name}"
                    owner_message = f"O evento {event.name} acontece amanhã. Já podes confirmar os últimos detalhes."
                else:
                    owner_title = f"Faltam {days_left} dias para o evento {event.name}"
                    owner_message = f"O evento {event.name} acontece em {days_left} dias. Acompanha a lista de convidados e os preparativos."

                owner_reminder_key = f"user-{owner.id}-event-{event.id}-days-{days_left}"

                notification, created = Notification.objects.get_or_create(
                    reminder_key=owner_reminder_key,
                    defaults={
                        'user': owner,
                        'event': event,
                        'title': owner_title,
                        'message': owner_message,
                        'days_left': days_left,
                    }
                )

                if created:
                    created_count += 1

                    if owner.email:
                        subject = owner_title
                        body = (
                            f"Olá {owner.username},\n\n"
                            f"{owner_message}\n\n"
                            f"Evento: {event.name}\n"
                            f"Data: {event.date}\n"
                            f"Local: {event.location or 'Não informado'}\n\n"
                            f"Kixanu"
                        )

                        email = EmailMultiAlternatives(
                            subject=subject,
                            body=body,
                            to=[owner.email]
                        )
                        email.send()
                        organizer_email_count += 1

            # Lembretes dos convidados confirmados
            if days_left in guest_reminder_days:
                confirmed_guests = Guest.objects.filter(
                    event=event,
                    status='confirmado'
                ).exclude(email__isnull=True).exclude(email__exact='')

                for guest in confirmed_guests:
                    if days_left == 0:
                        guest_title = f"O evento {event.name} é hoje"
                        guest_message = (
                            f"O evento {event.name} acontece hoje. "
                            f"Segue este lembrete final com o teu QR code de acesso."
                        )
                    elif days_left == 1:
                        guest_title = f"Falta 1 dia para o evento {event.name}"
                        guest_message = f"O evento {event.name} acontece amanhã. Guarda este lembrete para não esqueceres."
                    else:
                        guest_title = f"Faltam {days_left} dias para o evento {event.name}"
                        guest_message = f"O evento {event.name} acontece em {days_left} dias. Guardamos este lembrete para ti."

                    guest_reminder_key = f"guest-{guest.id}-event-{event.id}-days-{days_left}"

                    notification, created = Notification.objects.get_or_create(
                        reminder_key=guest_reminder_key,
                        defaults={
                            'user': owner,
                            'event': event,
                            'title': guest_title,
                            'message': f"Lembrete enviado ao convidado {guest.full_name}.",
                            'days_left': days_left,
                        }
                    )

                    if not created:
                        continue

                    created_count += 1

                    invite_link = f"/invite/{guest.token}/"

                    body = (
                        f"Olá {guest.full_name},\n\n"
                        f"{guest_message}\n\n"
                        f"Evento: {event.name}\n"
                        f"Data: {event.date}\n"
                        f"Local: {event.location or 'Não informado'}\n"
                    )

                    if event.description:
                        body += f"Descrição: {event.description}\n"

                    if event.allowed_companions > 0:
                        body += "\nEste convite permite acompanhante.\n"

                    body += (
                        f"\nPodes consultar o teu convite aqui:\n"
                        f"{invite_link}\n\n"
                        f"Kixanu"
                    )

                    email = EmailMultiAlternatives(
                        subject=guest_title,
                        body=body,
                        to=[guest.email]
                    )

                    if days_left == 0:
                        if not guest.qr_code:
                            generate_qr_for_guest(guest)
                            guest.refresh_from_db()

                        if guest.qr_code and guest.qr_code.path:
                            with open(guest.qr_code.path, 'rb') as qr_file:
                                email.attach(
                                    filename=f"qr_convite_{guest.id}.png",
                                    content=qr_file.read(),
                                    mimetype='image/png'
                                )

                    email.send()
                    guest_email_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Notificações criadas: {created_count} | Emails organizador: {organizer_email_count} | Emails convidados: {guest_email_count}"
            )
        )