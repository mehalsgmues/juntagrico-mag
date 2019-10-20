from django import template
from juntagrico_proactive.config import ProactiveConfig

register = template.Library()


@register.simple_tag
def vocabulary(key):
    return ProactiveConfig.vocabulary(key)
