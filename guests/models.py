from django.db import models
from django.utils.text import slugify
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
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    companion_name = models.CharField(max_length=255, blank=True, null=True)

    def _generate_unique_slug(self):
        base_slug = slugify(self.full_name) or "convidado"
        unique_part = str(self.token).replace("-", "")
        slug = f"{base_slug}-{unique_part}"

        counter = 1
        while Guest.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base_slug}-{unique_part}-{counter}"
            counter += 1

        return slug

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = uuid.uuid4()

        if not self.slug:
            self.slug = self._generate_unique_slug()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name