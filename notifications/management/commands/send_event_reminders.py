from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from notifications.models import Notification
from events.models import Event


class Command(BaseCommand):
    help = 'Cria notificações e envia lembretes por email sobre eventos próximos.'

    def handle(self, *args, **kwargs):
        today = timezone.localdate()
        reminder_days = [7, 3, 1, 0]

        events = Event.objects.exclude(owner__isnull=True)

        created_count = 0
        email_count = 0

        for event in events:
            if not event.date:
                continue

            days_left = (event.date - today).days

            if days_left not in reminder_days:
                continue

            owner = event.owner
            if not owner:
                continue

            if days_left == 0:
                title = f"O evento {event.name} é hoje"
                message = f"O evento {event.name} acontece hoje. Verifica os convidados e os preparativos finais."
            elif days_left == 1:
                title = f"Falta 1 dia para o evento {event.name}"
                message = f"O evento {event.name} acontece amanhã. Já podes confirmar os últimos detalhes."
            else:
                title = f"Faltam {days_left} dias para o evento {event.name}"
                message = f"O evento {event.name} acontece em {days_left} dias. Acompanha a lista de convidados e os preparativos."

            reminder_key = f"user-{owner.id}-event-{event.id}-days-{days_left}"

            notification, created = Notification.objects.get_or_create(
                reminder_key=reminder_key,
                defaults={
                    'user': owner,
                    'event': event,
                    'title': title,
                    'message': message,
                    'days_left': days_left,
                }
            )

            if created:
                created_count += 1

                if owner.email:
                    subject = title
                    body = (
                        f"Olá {owner.username},\n\n"
                        f"{message}\n\n"
                        f"Evento: {event.name}\n"
                        f"Data: {event.date}\n"
                        f"Local: {event.location or 'Não informado'}\n\n"
                        f"InvitePro"
                    )

                    email = EmailMultiAlternatives(
                        subject=subject,
                        body=body,
                        to=[owner.email]
                    )
                    email.send()
                    email_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Notificações criadas: {created_count} | Emails enviados: {email_count}"
            )
        )