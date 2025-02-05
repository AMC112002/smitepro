from django.db import models
from django.contrib.postgres.fields import JSONField  # Solo necesario en versiones antiguas de Django (<3.1)

class ItemCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Item(models.Model):
    TIER_CHOICES = [
        (1, "Tier 1"),
        (2, "Tier 2"),
        (3, "Tier 3"),
        ("Glyph", "Glifo"),
    ]

    name = models.CharField(max_length=100, unique=True)  # Nombre del objeto
    description = models.TextField(blank=True)  # Descripción del objeto
    price = models.PositiveIntegerField()  # Precio base en oro del objeto
    total_price = models.PositiveIntegerField(blank=True, null=True)  # Precio total considerando los ítems previos
    tier = models.IntegerField(choices=TIER_CHOICES, null=True, blank=True)  # Nivel del objeto (opcional)
    categories = models.ManyToManyField(ItemCategory, related_name="items")  # Categorías a las que pertenece el objeto
    image = models.ImageField(upload_to='items/', null=True, blank=True)  # Imagen del objeto

    # Relación de progresión
    from_item = models.ForeignKey(
        'self', 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL, 
        related_name='upgrades'
    )  # Indica de qué objeto proviene este en la progresión de tiers

    # Campo JSON para estadísticas del objeto
    stats = models.JSONField(default=dict, blank=True)  

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """
        Calcula el precio total basado en el costo del objeto más su predecesor (si tiene uno).
        """
        if self.from_item:
            self.total_price = self.price + self.from_item.total_price
        else:
            self.total_price = self.price

        super().save(*args, **kwargs)
