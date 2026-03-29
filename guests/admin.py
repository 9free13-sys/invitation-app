from django.contrib import admin
from .models import Guest


@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'event', 'phone', 'email', 'status')
    list_filter = ('event', 'status')
    search_fields = ('full_name', 'phone', 'email')