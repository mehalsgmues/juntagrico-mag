from datetime import datetime, timedelta

import requests
from dateutil.relativedelta import relativedelta
from django.db.models import Sum
from django.utils import timezone
from juntagrico.dao.subscriptiondao import SubscriptionDao
from juntagrico.entity.subs import SubscriptionPart
from juntagrico.util.models import q_canceled, q_deactivated

from mehalsgmues import settings


def date_from_get(request, name, default, date_format="%Y-%m-%d"):
    date = request.GET.get(name, None)
    if date is not None:
        return datetime.strptime(date, date_format).date()
    year = request.GET.get(name + '_year', None)
    if year is not None:
        month = request.GET.get(name + '_month', 1)
        day = request.GET.get(name + '_day', 1)
        try:
            return datetime(int(year), int(month), int(day)).date()
        except ValueError:
            return default
    return default


def get_delivery_dates_of_month(delivery_weekday, date):
    """
    yields all delivery dates of a month
    :param delivery_weekday: 0 = Monday, 6 = Sunday
    :param date: the start date to create deliveries for
    :return:
    """
    next_delivery = date + relativedelta(weekday=delivery_weekday)
    month = next_delivery.month
    # a special year
    if next_delivery == datetime(2023, 4, 7).date():
        next_delivery = next_delivery - timedelta(days=7)
    yield next_delivery
    while True:
        next_delivery = next_delivery + timedelta(days=7)
        if next_delivery.month == month:
            yield next_delivery
        else:
            break


def forum_notifications(user):
    api_key = getattr(settings, "DISCOURSE_API_KEY", None)
    if not api_key:
        return 0

    cache = forum_notifications.cache.get(user, None)
    if cache and cache[0] + timedelta(minutes=5) > timezone.now():
        return cache[1]

    base = "https://forum.mehalsgmues.ch/"
    method = base + "u/by-external/" + str(user.id) + ".json"
    headers = {
        'Api-Key': api_key,
        'Api-Username': 'system'
    }
    try:
        response = requests.get(method, headers=headers)
    except (requests.ConnectionError, requests.ConnectTimeout):
        return None
    if response:
        try:
            username = response.json()['user']['username']
        except (ValueError, KeyError):
            forum_notifications.cache[user] = (timezone.now(), None)
            return None
        # now with the username get notifications
        method = base + "session/current.json"
        headers['Api-Username'] = username
        try:
            response = requests.get(method, headers=headers)
        except (requests.ConnectionError, requests.ConnectTimeout):
            return None
        if response:
            try:
                current_user = response.json()['current_user']
                notifications = current_user['unread_notifications'] + current_user[
                    'unread_high_priority_notifications']
                forum_notifications.cache[user] = (timezone.now(), notifications)
                return notifications
            except (ValueError, KeyError):
                forum_notifications.cache[user] = (timezone.now(), None)


forum_notifications.cache = {}


def get_available_subscriptions():
    goal = int(getattr(settings, "SUBSCRIPTION_PROGRESS_GOAL", "10") or "10")
    target = SubscriptionPart.objects.filter(
        ~q_canceled() & ~q_deactivated(),
        type__size__product__is_extra=False,
        subscription__in=SubscriptionDao.future_subscriptions()
    ).aggregate(total=Sum('type__size__units'))['total'] or 0
    return goal - target
