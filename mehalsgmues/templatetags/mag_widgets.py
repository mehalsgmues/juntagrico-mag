from django import template
from django.utils.safestring import mark_safe

from mehalsgmues.utils.utils import draw_share_progress
from mehalsgmues.utils.news import get_recent_posts

register = template.Library()


@register.simple_tag
def share_progress():
    return mark_safe(draw_share_progress())


@register.simple_tag
def news():
    return mark_safe(get_recent_posts())


@register.simple_tag
def covid_info():
    return mark_safe('<div class="alert alert-success">Bitte beachte unsere aktuellen '
                     '<a href="https://mehalsgmues.ch/corona" target="_blank">Corona-Massnamen</a></div>')
