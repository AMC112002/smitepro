from django.db import models
from django.contrib.auth.models import User

# Extending user model to add extra fields
class Account(models.Model):
    IMP = 'imp'
    GESTOR_HOTEL = 'gestor_hotel'
    GESTOR_RECEPCIONES = 'gestor_recepciones'
    GESTOR_RESTAURANTES = 'gestor_restaurantes'

    ROLE_CHOICES = [
        (IMP, 'IMP'),
        (GESTOR_HOTEL, 'Gestor de Hoteles'),
        (GESTOR_RECEPCIONES, 'Gestor de Recepciones'),
        (GESTOR_RESTAURANTES, 'Gestor de Restaurantes'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=GESTOR_HOTEL)
    telephone = models.CharField(max_length=100)
    address = models.TextField(max_length=200)

    def __str__(self):
        return self.user.username