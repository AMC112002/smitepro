from django.core.management.base import BaseCommand
from objetos.models import Item, ItemCategory

class Command(BaseCommand):
    help = "Crea consumibles en la base de datos"

    def handle(self, *args, **kwargs):
        consumibles = [
            ("Baba's Brew", "Bebida de Baba"),
            ("Runic Bomb", "Bomba Rúnica"),
            ("Healing Potion", "Poción de Curación"),
            ("Mana Potion", "Poción de Maná"),
            ("Multi Potion", "Poción Múltiple"),
            ("Ward", "Centinela"),
            ("Proximity Ward", "Centinela de Proximidad"),
            ("Raven Ward", "Centinela Cuervo"),
            ("Sentry Ward", "Centinela de Vigilancia"),
            ("Baron's Brew", "Breve del Barón"),
            ("Chalice of Healing", "Cáliz de Curación"),
            ("Chalice of the Oracle", "Cáliz del Oráculo"),
            ("Potion of Power", "Poción de Poder"),
            ("Elixir of Defense", "Elixir de Defensa"),
            ("Elixir of Power", "Elixir de Poder"),
        ]

        # Obtener la categoría "Consumable"
        categoria, created = ItemCategory.objects.get_or_create(name="Consumable")

        for eng_name, esp_name in consumibles:
            item, created = Item.objects.get_or_create(
                name=esp_name,
                defaults={
                    "description": f"{esp_name} - Objeto consumible",
                    "price": 50,  # Puedes ajustar el precio si es necesario
                    "tier": 1,  # Todos los consumibles suelen ser de Tier 1
                }
            )
            item.categories.add(categoria)
            self.stdout.write(self.style.SUCCESS(f"{'Creado' if created else 'Ya existe'}: {esp_name}"))

        self.stdout.write(self.style.SUCCESS("Consumibles creados correctamente"))
