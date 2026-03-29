from django.contrib import admin
from django.utils.html import format_html
from .models import Guest


@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'event', 'phone', 'status', 'invite_link')
    readonly_fields = ('token',)

    def invite_link(self, obj):
        url = f"https://invitation-app-auto.onrender.com/invite/{obj.token}/confirm/"
        return format_html('<a href="{}" target="_blank">Link</a>', url)

    invite_link.short_description = "Convite"