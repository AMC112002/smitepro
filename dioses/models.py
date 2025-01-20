from django.db import models

class Ability(models.Model):
    name = models.CharField(max_length=100)  # Nombre de la habilidad
    ability_type = models.CharField(
        max_length=50,
        choices=[
            ('Active 1', 'Habilidad Activa 1'),
            ('Active 2', 'Habilidad Activa 2'),
            ('Active 3', 'Habilidad Activa 3'),
            ('Active 4', 'Habilidad Activa 4'),
            ('Passive', 'Habilidad Pasiva'),
        ]
    )  # Tipo de habilidad (activa o pasiva)
    description = models.TextField(blank=True)  # Descripción de la habilidad
    range = models.FloatField()  # Alcance de la habilidad
    radius = models.FloatField()  # Radio de área de efecto (si aplica)
    image = models.ImageField(upload_to='abilities/', null=True, blank=True)  # Imagen representativa de la habilidad

    def __str__(self):
        return self.name

class God(models.Model):
    #Enumerado para el panteón
    PANTHEON_CHOICES = [
        ('Chinese', 'Chino'),
        ('Egyptian', 'Egipcio'),
        ('Greek', 'Griego'),
        ('Hindu', 'Hindú'),
        ('Mayan', 'Maya'),
        ('Norse', 'Nórdico'),
        ('Roman', 'Romano'),
        ('Japanese', 'Japonés'),
        ('Celtic', 'Celta'),
        ('Slavic', 'Eslavo'),
        ('Voodoo', 'Vudú'),
        ('Polynesian', 'Polinesio'),
        ('Arthurian', 'Artúrico'),
        ('Babylonian', 'Babilonio'),
        ('Yoruba', 'Yoruba'),
        ('Great Old Ones', 'Grandes Antiguos'),
    ]

    # Enumerado para la dificultad
    DIFFICULTY_CHOICES = [
        ('Easy', 'Fácil'),
        ('Medium', 'Media'),
        ('Hard', 'Difícil'),
    ]

    # Enumerado para el tipo de poder
    POWER_CHOICES = [
        ('Physical', 'Físico'),
        ('Magical', 'Mágico'),
    ]

    # Atributos básicos
    name = models.CharField(max_length=100, unique=True)  # Nombre del dios
    pantheon = models.CharField(
        max_length=50,
        choices=PANTHEON_CHOICES
    )  # Panteón mitológico

    role = models.CharField(
        max_length=20,
        choices=[
            ('Hunter', 'Cazador'),
            ('Guardian', 'Guardían'),
            ('Mage', 'Mago'),
            ('Warrior', 'Guerrero'),
            ('Assassin', 'Asesino'),
        ]
    )  # Rol en el juego

    difficulty = models.CharField(
        max_length=10,
        choices=DIFFICULTY_CHOICES
    ) 

    # Estadísticas clave
    health = models.CharField(max_length=50)         # Salud base (e.g., "450 (+80)")
    mana = models.CharField(max_length=50)           # Maná base (e.g., "200 (+35)")
    speed = models.CharField(max_length=50)          # Velocidad de movimiento (e.g., "370")
    power = models.CharField(
        max_length=10,
        choices=POWER_CHOICES
    )  # Tipo de poder (físico o mágico)
    damage = models.CharField(max_length=50)         # Daño base (e.g., "34 (+1.45)")
    attack_speed = models.CharField(max_length=50)   # Velocidad de ataque base (e.g., "1.00 (+0.02)")

    # Nuevos atributos
    progresion = models.CharField(max_length=50)  # Progresión (e.g., "Escalabilidad", "Escala bien en late game")
    proteccion_fisica = models.CharField(max_length=50)  # Protección física
    proteccion_magica = models.CharField(max_length=50)  # Protección mágica
    hp5 = models.CharField(max_length=50)  # HP por segundo (recuperación de salud)
    mp5 = models.CharField(max_length=50)  # MP por segundo (recuperación de maná)

    # Relación con el modelo de habilidades
    abilities = models.ManyToManyField('Ability')  # Relación muchos a muchos con las habilidades

    # Información adicional
    lore = models.TextField(blank=True)           # Historia o trasfondo del dios
    image = models.ImageField(upload_to='gods/', null=True, blank=True)  # Imagen del dios

    def __str__(self):
        return self.name
