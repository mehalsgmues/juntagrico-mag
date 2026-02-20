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
    return emoji.replace_emoji(string, replace='')


@register.filter
def clean_url(url):
    return url.replace("https://", "").replace("http://", "")


@register.filter
def simple_link(url):
    return mark_safe(f'<a href="{url}" target="_blank">{clean_url(url)}</a>')


@register.simple_tag
def bar(name, active, required, target):
    segments = []
    target = target or 0
    total = max((active, required, target))
    required_width = required
    target_width = target

    if active < required:
        reached = ' bar-below-required'
    elif active < target:
        reached = ' bar-below-target'
    else:
        reached = ''

    # if required not reached
    if active < required:
        segments.append(f'<div class="bar-segment bar-active" style="width: {active / total * 100}%;">{active}</div>')
        required_width -= active
    # required segment
    segments.append(f'<div class="bar-segment bar-required" style="width: {required_width / total * 100}%;">{required}</div>')
    # if target not reached
    if reached and required < active < target:
        segments.append(f'<div class="bar-segment bar-active bar-below-target"'
                        f'style="width: {(active - required) / total * 100}%;">{active}</div>')
        target_width -= active
    else:
        target_width -= required
    # target segment
    if target > active:
        segments.append(f'<div class="bar-segment bar-target" '
                        f'style="width: {target_width / total * 100}%;">{target}</div>')
    elif active > required:
        segments.append(f'<div class="bar-segment bar-active bar-above-target"'
                        f'style="width: {(active - required) / total * 100}%;">{active}</div>')

    # bottom labels: required & target
    target_label = f'<div class="bar-label bar-target-label bar-label-left"' \
                   f'style="width: {(target - required) / total * 100}%;">Ziel</div>' if target > required and target > active else ''
    required_width = required / total * 100
    if required_width > 50:
        label = f'<div class="bar-label bar-required-label bar-label-left"' \
                f'style="width: {required_width}%;">Mindestens</div>'
    else:
        label = f'<div class="bar-label bar-required-right bar-label-right"' \
                f'style="left: {required_width}%; width: {required_width}%;">Mindestens</div>'
    labels_bottom = f'<div class="bar-labels bar-labels-bottom">{label}{target_label}</div>'

    # top label: active
    active_width = active / total * 100
    if active_width > 50:
        label = f'<div class="bar-label bar-active-label bar-label-left"' \
                f'style="width: {active_width}%;">Aktiv</div>'
    else:
        label = f'<div class="bar-label bar-active-label bar-label-right"' \
                f'style="left: {active_width}%; width: {active_width}%;">Aktiv</div>'
    labels_top = f'<div class="bar-labels bar-labels-top">{label}</div>'

    # bar
    return mark_safe(f'{labels_top}<div class="{name}-bar bar{reached}">{"".join(segments)}</div>{labels_bottom}')
