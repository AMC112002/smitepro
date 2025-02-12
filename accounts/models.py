from django.db import models
from django.contrib.auth.models import User

# Extending user model to add extra fields
class Account(models.Model):
    ADMIN = 'Administrador'
    USER = 'Usuario'

    ROLE_CHOICES = [
        (ADMIN, 'Administrador'),
        (USER, 'Usuario'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=USER)
    telephone = models.CharField(max_length=100)
    address = models.TextField(max_length=200)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def __str__(self):
        return self.user.username