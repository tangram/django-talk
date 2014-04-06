from django import template
from models import MessageIndex

register = template.Library()


@register.simple_tag
def pm_unread_count(user):
    return MessageIndex.objects.count_unread(user)
