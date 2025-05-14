# En tu archivo custom_filters.py (crea uno si no existe)
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)