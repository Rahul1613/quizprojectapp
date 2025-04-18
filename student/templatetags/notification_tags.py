from django import template
from datetime import timedelta

register = template.Library()

@register.filter
def add_hours(value, hours=1):
    """Add a specified number of hours to a datetime value."""
    try:
        return value + timedelta(hours=int(hours))
    except (ValueError, TypeError):
        return value
