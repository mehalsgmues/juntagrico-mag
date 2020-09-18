from django import template
import emoji

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
