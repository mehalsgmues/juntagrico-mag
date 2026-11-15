from django import template
from django.contrib.admin.sites import site as default_site
from django.conf import settings

from juntagrico.entity.jobs import RecuringJob

register = template.Library()


@register.filter
def isRecuring(job):
    return type(job) is RecuringJob


@register.filter
def breakFirstPage(index, limit):
    # to be used before breakNextPages
    if limit is None:
        return False
    elif index == limit:
        return True
    elif index > limit:
        return index - limit
    else:
        return False


@register.filter
def breakNextPages(index, limit):
    # to be used after breakFirstPage
    if index is True or index is False:
        return index
    elif limit is None:
        return False
    else:
        return index % limit == 0


@register.filter
def sort_by_name(subscriptions):
    return subscriptions.order_by('primary_member__first_name')


@register.simple_tag
def telegram_link():
    group_id = getattr(settings, "TELEGRAM_GROUP_LINK", "")
    if group_id:
        return f"https://t.me/joinchat/{group_id}"
    return "#"


@register.simple_tag(takes_context=True)
def can_open_admin(context):
    request = context.get("request")
    if request is None:
        return False

    site = default_site
    return site.has_permission(request)
