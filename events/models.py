from django.db import models


class Event(models.Model):
    EVENT_TYPES = [
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

    name = models.CharField(max_length=200)
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES)
    custom_event_type = models.CharField(max_length=100, blank=True)
    date = models.DateField()
    location = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def event_type_label(self):
        if self.event_type == 'outro' and self.custom_event_type:
            return self.custom_event_type
        return self.get_event_type_display()

    def __str__(self):
        return self.name