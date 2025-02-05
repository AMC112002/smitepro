from django.core.management.base import BaseCommand
from objetos.models import ItemCategory  # Asegúrate de que la app donde está el modelo se llama 'objetos'

CATEGORIES = [
    "Starter", "Relic", "Consumable", "Shards", "Magical Power", "Physical Power", 
    "Attack Speed", "Cooldown", "Critical Strike Chance", "Crowd Control Reduction", 
    "Health", "HP5", "Magical Lifesteal", "Magical Penetration", "Magical Protection", 
    "Mana", "Movement Speed", "MP5", "Physical Lifesteal", "Physical Penetration", "Physical Protection"
]

class Command(BaseCommand):
    help = "Crea las categorías de los objetos en la base de datos"

    def handle(self, *args, **kwargs):
        for category in CATEGORIES:
            obj, created = ItemCategory.objects.get_or_create(name=category)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Categoría creada: {category}'))
            else:
                self.stdout.write(self.style.WARNING(f'Categoría ya existente: {category}'))
