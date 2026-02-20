from django.contrib import admin
from .models import PosMachine

# Register your models here.
@admin.register(PosMachine)
class PosMachineAdmin(admin.ModelAdmin):
    list_display = ('pos_id', 'ip_address', 'is_online', 'last_seen')
    search_fields = ('pos_id', 'ip_address')
    list_filter = ('last_seen',)