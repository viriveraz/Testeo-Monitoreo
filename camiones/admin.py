from django.contrib import admin
from .models import Camion, AsignacionChofer, Chofer, MensajePredefinido

admin.site.register(MensajePredefinido)
admin.site.register(Camion)
admin.site.register(AsignacionChofer)

@admin.register(Chofer)
class ChoferAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'rut', 'telefono')



