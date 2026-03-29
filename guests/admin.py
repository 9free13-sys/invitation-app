from django.contrib import admin
from .models import Guest
from django.utils.html import format_html

@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'event', 'phone', 'status', 'invite_link')
    readonly_fields = ('token',)

    def invite_link(self, obj):
        url = f"https://invitation-app-auto.onrender.com/invite/{obj.token}/confirm/"
        return format_html(f'<a href="{url}" target="_blank">Link</a>')

    invite_link.short_description = "Convite"