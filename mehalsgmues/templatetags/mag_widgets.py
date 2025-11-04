from django import template
from django.utils.safestring import mark_safe
from django.db.models import Sum
from juntagrico.entity.member import Member
from juntagrico.entity.subs import SubscriptionPart
from juntagrico.dao.subscriptiondao import SubscriptionDao
from juntagrico.util.models import q_isactive


from mapjob.models import MapJob
from mehalsgmues.utils.utils import get_available_subscriptions
from mehalsgmues.utils.news import get_recent_posts
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
    active_parts = SubscriptionPart.objects.filter(
        type__size__product__is_extra=False).filter(q_isactive()).filter(
        subscription__in=SubscriptionDao().all_active_subscritions()
    )

    eat_equivalent_price = float(getattr(settings, "EAT_EQUIVALENT_PRICE", "1200") or "1200")
    num_eat_equivalent = float(active_parts.filter(
            type__price__gt=0).aggregate(total=Sum('type__price'))['total']) / eat_equivalent_price
    target_num_eat = int(getattr(settings, "SUBSCRIPTION_PROGRESS_GOAL", "270") or "270")
    missing_eat = target_num_eat - num_eat_equivalent
    rotation = 1.8 * min(max(num_eat_equivalent - 200, 0), 100)
    return {
        'rotation': int(rotation),
        'target_num_eat': target_num_eat,
        'num_eat_equivalent': round(num_eat_equivalent, 1),
        'missing_eat': round(missing_eat, 1),
    }