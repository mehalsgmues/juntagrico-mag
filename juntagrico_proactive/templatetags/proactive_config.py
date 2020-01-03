from django import template
from juntagrico.config import Config

register = template.Library()


@register.simple_tag
def vocabulary(key):
    return Config.vocabulary(key)
