from django import template
from django.utils.safestring import mark_safe
from django.db.models import Sum
from juntagrico.entity.member import Member
from juntagrico.entity.subs import SubscriptionPart
from juntagrico.dao.subscriptiondao import SubscriptionDao


from mapjob.models import MapJob
from mehalsgmues.utils.utils import get_available_subscriptions
from mehalsgmues.utils.news import get_recent_posts
from mehalsgmues.utils.stats import get_active_parts, get_eat_stats
from mehalsgmues import settings


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


@register.inclusion_tag('mag/stats/subscription_counter.html')
def eat_counter():
    active_parts = get_active_parts()
    return get_eat_stats(active_parts)