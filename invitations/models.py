from django.db import models
from events.models import Event
from guests.models import Guest


class Invitation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('accepted', 'Aceitou'),
        ('declined', 'Recusou'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'guest')

    def __str__(self):
        return f"{self.guest} - {self.event}"