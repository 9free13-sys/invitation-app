from django.contrib import admin
from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_event_type', 'date', 'location', 'created_at')
    fields = ('name', 'event_type', 'custom_event_type', 'date', 'location', 'description')

    def display_event_type(self, obj):
        return obj.event_type_label()

    display_event_type.short_description = 'Tipo de evento'

    class Media:
        js = ('events/admin/event_admin.js',)