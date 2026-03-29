from django.contrib import admin
from django.utils.html import format_html
from urllib.parse import quote
from .models import Guest


@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'event', 'phone', 'status', 'invite_link', 'whatsapp_link')
    readonly_fields = ('token',)

    def invite_link(self, obj):
        url = f"https://invitation-app-auto.onrender.com/invite/{obj.token}/confirm/"
        return format_html('<a href="{}" target="_blank">Link</a>', url)
    invite_link.short_description = "Convite"

    def whatsapp_link(self, obj):
        invite_url = f"https://invitation-app-auto.onrender.com/invite/{obj.token}/confirm/"
        phone = str(obj.phone).replace(" ", "").replace("+", "")
        if phone.startswith("0"):
            phone = phone[1:]
        if not phone.startswith("244"):
            phone = "244" + phone

        message = (
            f"Olá {obj.full_name},\n\n"
            f"Você está convidado(a) para o evento *{obj.event.name}*.\n"
            f"Para confirmar a sua presença, clique no link abaixo:\n"
            f"{invite_url}\n\n"
            f"Obrigado."
    )
        wa_url = f"https://wa.me/{phone}?text={quote(message)}"
        return format_html('<a href="{}" target="_blank">WhatsApp</a>', wa_url)
    whatsapp_link.short_description = "WhatsApp"