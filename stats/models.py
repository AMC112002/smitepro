from django.db import models
from dioses.models import God
from objetos.models import Item
from django.utils import timezone

class GodStat(models.Model):
    god = models.ForeignKey(God, on_delete=models.CASCADE)
    usage_count = models.IntegerField(default=0)
    win_rate = models.FloatField(default=0.0)
    last_updated = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.god.name} - Usage: {self.usage_count}"

class ItemStat(models.Model):
    USAGE_CHOICES = [
        ('starter', 'Starter Item'),
        ('passive', 'Passive Item'),
        ('relic', 'Relic'),
    ]
    
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    usage_count = models.IntegerField(default=0)
    usage_type = models.CharField(max_length=10, choices=USAGE_CHOICES)
    win_rate = models.FloatField(default=0.0)
    last_updated = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ('item', 'usage_type')
    
    def __str__(self):
        return f"{self.item.name} ({self.get_usage_type_display()}) - Usage: {self.usage_count}"