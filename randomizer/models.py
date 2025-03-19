from django.db import models

class RandomizerHistory(models.Model):
    """Modelo para guardar el historial de selecciones aleatorias"""
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True, blank=True)
    god = models.ForeignKey('dioses.God', on_delete=models.SET_NULL, null=True)
    build = models.ForeignKey('builds.Build', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Selección aleatoria para {self.user.username if self.user else 'Anónimo'} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"