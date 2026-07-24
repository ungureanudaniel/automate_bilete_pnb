from django.contrib import admin
from .models import PosMachine

@admin.register(PosMachine)
class PosMachineAdmin(admin.ModelAdmin):
    list_display = ('pos_id', 'name', 'ip_address', 'is_online', 'last_seen')
    search_fields = ('pos_id', 'name', 'ip_address')
    list_filter = ('last_seen',)
