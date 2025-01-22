from django import template

register = template.Library()

@register.filter
def dict_key(dictionary, key):
    """Devuelve el valor de un diccionario para la clave proporcionada."""
    return dictionary.get(key)
