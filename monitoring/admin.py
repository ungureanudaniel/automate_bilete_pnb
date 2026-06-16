from django.contrib import admin
from parameters.models import TicketMachine, Produs, Serie, Tranzactie, UserLegacy

@admin.register(TicketMachine)
class TicketMachineAdmin(admin.ModelAdmin):
    list_display = ('id', 'pos_id', 'is_online', 'ultima_conectare')
    search_fields = ('pos_id',)
    list_filter = ('is_online',)

@admin.register(Produs)
class ProdusAdmin(admin.ModelAdmin):
    list_display = ('id', 'nume', 'pret')
    search_fields = ('nume',)

@admin.register(Serie)
class SerieAdmin(admin.ModelAdmin):
    list_display = ('id', 'nume', 'data_creare')
    search_fields = ('nume',)
    ordering = ('-data_creare',)

@admin.register(Tranzactie)
class TranzactieAdmin(admin.ModelAdmin):
    list_display = ('id', 'ticket_machine', 'produs', 'cantitate', 'data_tranzactie')
    search_fields = ('ticket_machine__pos_id', 'produs__nume')
    list_filter = ('data_tranzactie',)

@admin.register(UserLegacy)
class UserLegacyAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email')
    search_fields = ('username', 'email')
    ordering = ('-created_at',)
