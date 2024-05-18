from django import template
from django.utils.safestring import mark_safe
from juntagrico.entity.member import Member

from mapjob.models import MapJob
from mehalsgmues.utils.utils import draw_share_progress, get_available_subscriptions
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
    return mark_safe('<div class="alert alert-success">Die bisher geltenden Corona-Massnahmen wurden wie in der '
                     'ganzen Schweiz auch bei meh als gmues grösstenteils ausser Kraft gesetzt. Es verbleiben die '
                     '<a href="https://mehalsgmues.ch/corona" target="_blank">Umgangsrichtlinien</a>.<br>'
                     'Bleibt umsichtig und freundlich zueinander :-)</div>'
                     )


@register.simple_tag
def available_subscriptions():
    return get_available_subscriptions()


@register.simple_tag
def member_and_phone(member):
    try:
        member = Member.objects.get(id=member)
        return f"{member.get_name()} {member.get_phone()}"
    except Member.DoesNotExist:
        return "(Unbekannter Benutzer)"


@register.simple_tag
def email_of(member):
    try:
        member = Member.objects.get(id=member)
        return member.email
    except Member.DoesNotExist:
        return ""


@register.simple_tag
def member_is_flyering(member):
    return MapJob.objects.filter(assignment__member=member).exclude(progress=MapJob.Progress.COMPLETE).exists()
