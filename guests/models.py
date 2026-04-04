from django.db import models
import uuid


class Guest(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('confirmado', 'Confirmado'),
        ('recusado', 'Recusado'),
    ]

    event = models.ForeignKey('events.Event', on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)

    # nome do acompanhante, opcional
    companion_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.full_name