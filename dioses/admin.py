from django.contrib import admin
from .models import God, Ability

class AbilityAdmin(admin.ModelAdmin):
    list_display = ('name', 'ability_type', 'associated_gods')  # Agrega la columna personalizada

    def associated_gods(self, obj):
        # Obtiene una lista de nombres de los dioses asociados a esta habilidad
        return ", ".join([god.name for god in obj.god_set.all()])
    associated_gods.short_description = "Dioses asociados"  # Nombre de la columna en el admin

# Registra los modelos con su configuración personalizada
admin.site.register(God)
admin.site.register(Ability, AbilityAdmin)
