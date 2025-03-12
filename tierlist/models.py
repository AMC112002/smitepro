from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from dioses.models import God
from django.urls import reverse

class TierList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tierlists')
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=True, verbose_name="Público")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Tier List"
        verbose_name_plural = "Tier Lists"
    
    def __str__(self):
        return f'{self.name} - {self.user.username}'
    
    def get_absolute_url(self):
        return reverse('tierlist_detail', kwargs={'pk': self.pk})
    
    def get_tier_counts(self):
        """Devuelve un conteo de dioses por tier"""
        counts = {}
        for choice in Tier.TIER_CHOICES:
            counts[choice[0]] = self.tiers.filter(tier=choice[0]).count()
        return counts

class Tier(models.Model):
    TIER_CHOICES = [
        ('S', 'S Tier'),
        ('A', 'A Tier'),
        ('B', 'B Tier'),
        ('C', 'C Tier'),
        ('D', 'D Tier'),
        ('F', 'F Tier'),
    ]
    
    tierlist = models.ForeignKey(TierList, on_delete=models.CASCADE, related_name='tiers')
    god = models.ForeignKey(God, on_delete=models.CASCADE, related_name='tier_placements')
    tier = models.CharField(max_length=1, choices=TIER_CHOICES)
    notes = models.CharField(max_length=200, blank=True, verbose_name="Notas")
    
    class Meta:
        unique_together = ('tierlist', 'god')
        ordering = ['tier']
    
    def __str__(self):
        return f'{self.god.name} - {self.get_tier_display()}'

class TierListComment(models.Model):
    tierlist = models.ForeignKey(TierList, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(verbose_name="Comentario")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Comentario por {self.user.username} en {self.tierlist.name}'