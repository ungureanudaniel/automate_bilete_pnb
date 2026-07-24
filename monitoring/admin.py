from django.contrib import admin
from parameters.models import TicketMachine, Produs, Serie, Tranzactie, UserLegacy

@admin.register(Produs)
class ProdusAdmin(admin.ModelAdmin):
    list_display = ('denumire', 'pret')
    search_fields = ('denumire',)

@admin.register(Serie)
class SerieAdmin(admin.ModelAdmin):
    list_display = ('serie', 'numar', 'locatie_pos')
    search_fields = ('serie',)
    ordering = ('-serie',)

@admin.register(Tranzactie)
class TranzactieAdmin(admin.ModelAdmin):
    list_display = ('id_produs', 'pos_id', 'cantitate', 'data_tranzactie')
    search_fields = ('pos_id', 'id_produs')
    list_filter = ('data_tranzactie',)

@admin.register(UserLegacy)
class UserLegacyAdmin(admin.ModelAdmin):
    list_display = ('nume', 'tip')
    search_fields = ('nume', 'tip')
