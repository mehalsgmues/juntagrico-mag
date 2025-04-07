from django import template
from django.utils.safestring import mark_safe
from juntagrico.entity.member import Member

from mapjob.models import MapJob
from mehalsgmues.utils.utils import get_available_subscriptions
from mehalsgmues.utils.news import get_recent_posts

register = template.Library()


@register.simple_tag
def news():
    return mark_safe(get_recent_posts())


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
