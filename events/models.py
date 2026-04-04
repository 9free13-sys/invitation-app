from django.db import models
from django.contrib.auth.models import User


class Event(models.Model):
    EVENT_TYPE_CHOICES = [
        ('aniversario', 'Aniversário'),
        ('casamento', 'Casamento'),
        ('noivado', 'Noivado'),
        ('baptizado', 'Baptizado'),
        ('cha_de_bebe', 'Chá de bebé'),
        ('formatura', 'Formatura'),
        ('conferencia', 'Conferência'),
        ('reuniao', 'Reunião'),
        ('evento_corporativo', 'Evento corporativo'),
        ('outro', 'Outro'),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPE_CHOICES, default='outro')
    date = models.DateField()
    location = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    # novo campo: regra global do evento
    allowed_companions = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

    @property
    def event_type_label(self):
        event_type_map = dict(self.EVENT_TYPE_CHOICES)
        return event_type_map.get(self.event_type, self.event_type)