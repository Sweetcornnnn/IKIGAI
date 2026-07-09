from django import template

register = template.Library()

@register.filter
def attr(obj, attr_name):
    """Get attribute from object safely"""
    if obj is None:
        return None
    if hasattr(obj, attr_name):
        value = getattr(obj, attr_name)
        if callable(value):
            return value()
        return value
    return None

@register.filter
def get_item(dictionary, key):
    if dictionary is None:
        return None
    return dictionary.get(key)

@register.filter
def get_field(obj, field_name):
    if obj is None:
        return None
    return obj._meta.get_field(field_name)