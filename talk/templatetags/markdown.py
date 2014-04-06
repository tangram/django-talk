from django import template
from django.utils.safestring import mark_safe
import mistune

register = template.Library()


@register.filter
def markdown(value):
    html = mistune.markdown(value)
    return mark_safe(html)
