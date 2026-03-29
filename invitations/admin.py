from django.contrib import admin
from .models import Invitation


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ('event', 'guest', 'status', 'sent_at')
    list_filter = ('status', 'event')
    search_fields = ('guest__full_name', 'guest__document_id', 'event__name')
    ordering = ('-sent_at',)