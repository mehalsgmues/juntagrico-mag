# -*- coding: utf-8 -*-

from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse

from juntagrico.models import Member

from juntagrico.dao.depotdao import DepotDao
from juntagrico.dao.listmessagedao import ListMessageDao
from juntagrico.dao.subscriptionsizedao import SubscriptionSizeDao
from juntagrico.util.pdf import render_to_pdf_http
from juntagrico.util.temporal import weekdays
from django.utils import timezone

# API    
@staff_member_required
def api_emaillist(request):
    """prints comma separated list of member emails"""
    # get emails
    return HttpResponse(', '.join(Member.objects.filter(inactive=False).values_list('email', flat=True)))


# pdf
def generate_pdf_dict(forDepotList=False):
    depots = DepotDao.all_depots_order_by_code()

    subscription_names = []
    for subscription_size in SubscriptionSizeDao.sizes_for_depot_list():
        subscription_names.append(subscription_size.name)

    used_weekdays = []
    for item in DepotDao.distinct_weekdays():
        used_weekdays.append(weekdays[item['weekday']])

    overview = {
        'all': None
    }
    for weekday in used_weekdays:
        overview[weekday] = None

    count = len(subscription_names)
    for weekday in used_weekdays:
        overview[weekday] = [0] * count
    overview['all'] = [0] * count

    all = overview.get('all')

    for depot in depots:
        depot.fill_overview_cache()
        row = overview.get(depot.get_weekday_display())
        count = 0
        # noinspection PyTypeChecker
        while count < len(row):
            row[count] += depot.overview_cache[count]
            all[count] += depot.overview_cache[count]
            count += 1
        if forDepotList:
            # append sub_size_name
            depot.overview_cache = zip( subscription_names, depot.overview_cache )
            # sort subs by name of primary member
            depot.subscription_cache = depot.subscription_cache.order_by('primary_member__first_name', 'primary_member__last_name')

    insert_point = len(subscription_names)
    for weekday in used_weekdays:
        overview[weekday].insert(insert_point, 0)
    overview['all'].insert(insert_point, 0)

    index = 0
    for subscription_size in SubscriptionSizeDao.sizes_for_depot_list():
        for weekday in used_weekdays:
            overview[weekday][insert_point] = overview[weekday][insert_point] + subscription_size.units * \
                                              overview[weekday][index]
        overview['all'][insert_point] = overview['all'][insert_point] + subscription_size.units * overview['all'][
            index]
        index += 1

    return {
        'overview': overview,
        'depots': depots,
        'subscription_names': subscription_names,
        'subscriptioncount': len(subscription_names) + 1,
        'datum': timezone.now(),
        'weekdays': used_weekdays,
        'messages': ListMessageDao.all_active()
    }


@staff_member_required
def depot_list(request):
    return render_to_pdf_http('exports/depotlist.html', generate_pdf_dict(True), 'depotlist.pdf')


@staff_member_required
def depot_overview(request):
    return render_to_pdf_http('exports/depot_overview.html', generate_pdf_dict(), 'depot_overview.pdf')


@staff_member_required
def amount_overview(request):
    return render_to_pdf_http('exports/amount_overview.html', generate_pdf_dict(), 'amount_overview.pdf')