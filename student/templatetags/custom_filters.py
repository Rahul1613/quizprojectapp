from django import template
from datetime import timedelta

register = template.Library()

@register.filter
def add_hours(value, hours):
    """Add given number of hours to a datetime value."""
    try:
        hours = int(hours)
        return value + timedelta(hours=hours)
    except (ValueError, TypeError):
        return value
