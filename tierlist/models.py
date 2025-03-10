from django.db import models
from django.contrib.auth.models import User
from dioses.models import God

class TierList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Usuario que crea la tierlist
    name = models.CharField(max_length=100)  # Nombre de la tierlist
    created_at = models.DateTimeField(auto_now_add=True)  # Fecha de creación

    def __str__(self):
        return f'{self.name} - {self.user.username}'

class Tier(models.Model):
    TIER_CHOICES = [
        ('S', 'S Tier'),
        ('A', 'A Tier'),
        ('B', 'B Tier'),
        ('C', 'C Tier'),
        ('D', 'D Tier'),
    ]
    
    tierlist = models.ForeignKey(TierList, on_delete=models.CASCADE, related_name='tiers')
    god = models.ForeignKey(God, on_delete=models.CASCADE)  # Dios asociado
    tier = models.CharField(max_length=1, choices=TIER_CHOICES)  # Tier asignado

    class Meta:
        unique_together = ('tierlist', 'god')  # Evitar que el mismo dios aparezca varias veces en una tierlist

    def __str__(self):
        return f'{self.god.name} - {self.get_tier_display()}'
