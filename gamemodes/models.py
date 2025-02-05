from django.db import models
import json

class JungleCamp(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

class GameMode(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='modes/', blank=True, null=True)
    statistics = models.JSONField(blank=True, null=True)
    resume = models.TextField(blank=True, null=True)
    minimap = models.ImageField(upload_to='minimaps/', blank=True, null=True)
    jungle_camps = models.ManyToManyField(JungleCamp, blank=True)  # Relación con JungleCamp
    unique_gameplay_mechanics = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
