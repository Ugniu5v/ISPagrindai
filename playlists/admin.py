from django.contrib import admin
from .models import Grojarastis, GrojarastisDaina, GrojarascioVertinimas


@admin.register(Grojarastis)
class GrojarastisAdmin(admin.ModelAdmin):
    list_display = ['pavadinimas', 'savininkas', 'yra_viesas', 'sukurimo_data']
    list_filter = ['yra_viesas', 'sukurimo_data', 'savininkas']
    search_fields = ['pavadinimas', 'savininkas__username', 'aprasymas']
    readonly_fields = ['sukurimo_data', 'atnaujinimo_data']


@admin.register(GrojarastisDaina)
class GrojarastisDainaAdmin(admin.ModelAdmin):
    list_display = ['grojarastis', 'eiles_nr', 'dainos_pavadinimas', 'atlikėjo_vardas']
    list_filter = ['grojarastis__pavadinimas']
    search_fields = ['dainos_pavadinimas', 'atlikėjo_vardas']
    ordering = ['grojarastis', 'eiles_nr']


@admin.register(GrojarascioVertinimas)
class GrojarascioVertinimasAdmin(admin.ModelAdmin):
    list_display = ['grojarastis', 'naudotojas', 'ivertinimas', 'ivertinimo_data']
    list_filter = ['ivertinimas', 'ivertinimo_data']
    readonly_fields = ['ivertinimo_data']