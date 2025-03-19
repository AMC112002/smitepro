from django.db import models
from django.contrib.auth.models import User
from dioses.models import God
from objetos.models import Item

class Build(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Usuario que crea la build
    god = models.ForeignKey(God, on_delete=models.CASCADE)  # Dios para la build
    starter_item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='starter_builds')
    passive_items = models.ManyToManyField(Item, related_name='passive_builds')
    relics = models.ManyToManyField(Item, related_name='relic_builds')
    is_random = models.BooleanField(default=False)  # ⭐ Nueva bandera para builds del randomizer

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.god.name} - {self.user.username}"
