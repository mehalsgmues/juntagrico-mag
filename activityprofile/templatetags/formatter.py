from django import template
import emoji
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def close_ul(string):
    if string.startswith('<ul>'):
        return string[4:]
    return '</ul>' + string


@register.filter
def demojize(string):
    """ skip emoji support for now, as the supported font types do not support color emojis
    """
    return emoji.get_emoji_regexp().sub('', string)


@register.filter
def clean_url(url):
    return url.replace("https://", "").replace("http://", "")


@register.filter
def simple_link(url):
    return mark_safe(f'<a href="{url}" target="_blank">{clean_url(url)}</a>')
