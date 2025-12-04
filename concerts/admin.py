from django.contrib import admin
from django.contrib import admin
from .models import Vieta, Koncertas, KoncertoDalyvis

@admin.register(Vieta)
class VietaAdmin(admin.ModelAdmin):
    list_display = ['pavadinimas', 'miestas', 'salis']
    search_fields = ['pavadinimas', 'miestas']

@admin.register(Koncertas)
class KoncertasAdmin(admin.ModelAdmin):
    list_display = ['pavadinimas', 'pradzios_data', 'zanras', 'vieta']
    list_filter = ['zanras', 'yra_atsauktas', 'yra_viesas']
    search_fields = ['pavadinimas', 'aprasymas']

@admin.register(KoncertoDalyvis)
class KoncertoDalyvvisAdmin(admin.ModelAdmin):
    list_display = ['vartotojas', 'koncertas', 'dalyvavimo_busena']
    list_filter = ['dalyvavimo_busena']
