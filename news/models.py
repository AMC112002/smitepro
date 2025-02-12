from django.db import models
from dioses.models import God, Ability
from objetos.models import Item

class PatchNotes(models.Model):
    title = models.CharField(max_length=255)
    publication_date = models.DateField()
    image = models.ImageField(upload_to='patch_notes/', blank=True, null=True)
    game_modes = models.TextField(help_text="Modos de juego actualizados", blank=True, null=True)

    # Relación con dioses que recibieron cambios
    god_balance = models.ManyToManyField('dioses.God', through='GodBalance', related_name='patches')

    # Relación con objetos que recibieron cambios
    item_balance = models.ManyToManyField('objetos.Item', through='ItemBalance', related_name='patches')

    new_god_skin = models.CharField(max_length=255, blank=True, null=True)
    new_voice_pack = models.CharField(max_length=255, blank=True, null=True)
    new_god_skin_voice_actors = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} - {self.publication_date}"


class GodBalance(models.Model):
    BUFF_NERF_CHOICES = [
        ('Buff', 'Buff'),
        ('Nerf', 'Nerf'),
    ]

    patch = models.ForeignKey(PatchNotes, on_delete=models.CASCADE)
    god = models.ForeignKey(God, on_delete=models.CASCADE)
    change_type = models.CharField(max_length=10, choices=BUFF_NERF_CHOICES)

    general_change = models.TextField(
        help_text="Cambios generales aplicados al dios", 
        blank=True, null=True
    )
    
    abilities_affected = models.ManyToManyField(
        'dioses.Ability', 
        blank=True, 
        through='AbilityBalance'
    )

    def __str__(self):
        return f"{self.get_change_type_display()} - {self.god.name} ({self.patch.title})"


class AbilityBalance(models.Model):
    god_balance = models.ForeignKey(GodBalance, on_delete=models.CASCADE)
    ability = models.ForeignKey(Ability, on_delete=models.CASCADE)
    change_description = models.TextField(help_text="Detalles del cambio en la habilidad")

    def __str__(self):
        return f"{self.ability.name} - {self.god_balance.god.name}"


class ItemBalance(models.Model):
    BUFF_NERF_CHOICES = [
        ('Buff', 'Buff'),
        ('Nerf', 'Nerf'),
    ]

    patch = models.ForeignKey(PatchNotes, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    change_description = models.TextField(help_text="Detalles del buff/nerf")
    change_type = models.CharField(max_length=10, choices=BUFF_NERF_CHOICES, default='Buff')

    def __str__(self):
        return f"{self.item.name} - {self.patch.title} ({self.change_type})"


class Event(models.Model):
    title = models.CharField(max_length=255)
    publication_date = models.DateField()
    image = models.ImageField(upload_to='events/', blank=True, null=True)
    description = models.TextField()
    standard_tracks = models.TextField()
    quests = models.JSONField(help_text="Quests organizadas por semanas")

    def __str__(self):
        return f"{self.title} - {self.publication_date}"
