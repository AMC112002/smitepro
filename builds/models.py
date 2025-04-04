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

    def average_rating(self):
        ratings = self.ratings.all()
        if ratings:
            return sum(r.rating for r in ratings) / len(ratings)
        return 0
    
    def total_ratings(self):
        return self.ratings.count()

class BuildRating(models.Model):
    build = models.ForeignKey(Build, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='build_ratings')
    rating = models.IntegerField(choices=[(1, '1 - Muy mala'), (2, '2 - Mala'), (3, '3 - Regular'), 
                                         (4, '4 - Buena'), (5, '5 - Excelente')])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Asegurar que un usuario solo pueda valorar una build una vez
        unique_together = ('build', 'user')

    def __str__(self):
        return f"{self.user.username} - {self.build.god.name} - {self.rating}"