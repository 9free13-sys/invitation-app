from django.contrib import admin
from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'event_type', 'date', 'location', 'owner')
    search_fields = ('name', 'location')
    list_filter = ('event_type', 'date')