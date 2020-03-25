from django import template
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
        return (index-limit)
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
