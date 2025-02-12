from django import template

register = template.Library()

@register.filter
def dict_key(dictionary, key):
    """Devuelve el valor de un diccionario para la clave proporcionada."""
    return dictionary.get(key)

@register.filter
def split(value, arg):
    return value.split(arg)

@register.filter(name="strip")
def strip(value):
    return value.strip() if isinstance(value, str) else value

