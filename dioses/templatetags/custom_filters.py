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

@register.filter
def replace_underscores(value):
    return value.replace('_', ' ')

@register.filter
def multiply(value, arg):
    """Multiplies the value by the argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''

@register.filter
def extract_base_stat(value):
    """Extracts the base value from a stat string like '385 (+80)'"""
    if isinstance(value, str):
        # Check if it's a string with a pattern like "385 (+80)"
        import re
        base_match = re.match(r'^(\d+)', value)
        if base_match:
            return int(base_match.group(1))
    try:
        # If it's already a number or can be converted to one
        return int(value)
    except (ValueError, TypeError):
        return 0
        
@register.filter
def stat_percent(value, divisor):
    """Calculates percentage for stat bars"""
    base_value = extract_base_stat(value)
    try:
        result = base_value / float(divisor)
        # Cap at 100%
        return min(result, 100)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter
def attack_speed_percent(value):
    """Calculate percentage for attack speed"""
    try:
        base_value = extract_base_stat(value)
        return min(base_value * 100 / 2, 100)  # Cap at 100%
    except (ValueError, TypeError):
        return 0