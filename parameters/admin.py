from django.contrib import admin

from django.contrib import admin
from .models import Produs, Serie, Tranzactie, PosPaper

@admin.register(Produs)
class ProdusAdmin(admin.ModelAdmin):
    list_display = ('id', 'denumire', 'pret', 'valabilitate_zile')
    search_fields = ('denumire',)

@admin.register(Serie)
class SerieAdmin(admin.ModelAdmin):
    list_display = ('serie', 'numar', 'locatie_pos')

@admin.register(Tranzactie)
class TranzactieAdmin(admin.ModelAdmin):
    list_display = ('id', 'pos_id', 'id_produs', 'cantitate', 'total', 'data_tranzactie', 'nr')
    list_filter = ('pos_id', 'data_tranzactie')
    readonly_fields = [f.name for f in Tranzactie._meta.fields]

@admin.register(PosPaper)
class PosPaperAdmin(admin.ModelAdmin):
    list_display = ('pos_id', 'tickets_at_last_change', 'roll_capacity', 'last_change')
    list_filter = ('pos_id', 'last_change')
    readonly_fields = [f.name for f in PosPaper._meta.fields]