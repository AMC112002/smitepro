from django import forms
from dioses.models import God

class RandomizerForm(forms.Form):
    """Formulario para filtrar la selección aleatoria de dioses"""
    
    # Obtener las opciones dinámicamente del modelo God
    pantheon = forms.ChoiceField(
        choices=[('', 'Todos los panteones')] + list(God.PANTHEON_CHOICES),
        required=False
    )
    
    role = forms.ChoiceField(
        choices=[
            ('', 'Todos los roles'),
            ('Hunter', 'Cazador'),
            ('Guardian', 'Guardián'),
            ('Mage', 'Mago'),
            ('Warrior', 'Guerrero'),
            ('Assassin', 'Asesino'),
        ],
        required=False
    )
    
    difficulty = forms.ChoiceField(
        choices=[('', 'Todas las dificultades')] + list(God.DIFFICULTY_CHOICES),
        required=False
    )