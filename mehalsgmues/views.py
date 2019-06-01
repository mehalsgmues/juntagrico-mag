from django.utils.safestring import mark_safe
from openpyxl import Workbook

from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse

from juntagrico.models import Member, Subscription

from juntagrico.dao.depotdao import DepotDao
from juntagrico.dao.listmessagedao import ListMessageDao
from juntagrico.dao.subscriptionsizedao import SubscriptionSizeDao
from juntagrico.util.pdf import render_to_pdf_http
from juntagrico.util.temporal import weekdays, start_of_business_year, end_of_business_year
from juntagrico.config import Config
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from mehalsgmues.utils.stats import assignments_by_subscription, assignments_by_day, slots_by_day
from mehalsgmues.utils.utils import date_from_get, get_delivery_dates_of_month


# API
@staff_member_required
def api_emaillist(request):
    """prints comma separated list of member emails"""
    # get emails
    return HttpResponse(', '.join(Member.objects.filter(inactive=False).values_list('email', flat=True)))


# pdf
def generate_pdf_dict(for_depot_list=False):
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
        if for_depot_list:
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


def other_recipients_names_w_linebreaks(self):
    members = self.recipients.exclude(email=self.primary_member.email)
    members = [str(member) for member in members]
    return mark_safe('<br>'.join([', '.join(members[x:x+6]) for x in range(0, len(members), 6)]))


@staff_member_required
def depot_list(request):
    renderdict = generate_pdf_dict(True)
    for depot in renderdict['depots']:
        depot.delivery_dates = list(get_delivery_dates_of_month(depot.weekday, int(request.GET.get('month', 0))))
    Subscription.other_recipients_names_w_linebreaks = other_recipients_names_w_linebreaks
    return render_to_pdf_http('exports/depotlist.html', renderdict, 'depotlist.pdf')


@staff_member_required
def depot_overview(request):
    return render_to_pdf_http('exports/depot_overview.html', generate_pdf_dict(), 'depot_overview.pdf')


@staff_member_required
def amount_overview(request):
    return render_to_pdf_http('exports/amount_overview.html', generate_pdf_dict(), 'amount_overview.pdf')


@staff_member_required
def stats(request):
    start_date = date_from_get(request, 'start_date', start_of_business_year())
    end_date = date_from_get(request, 'end_date', end_of_business_year())

    filename = '{}_{}_stats.xlsx'.format(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=' + filename
    wb = Workbook()

    # Sheet 1: assignments by subscription
    ws1 = wb.active
    ws1.title = "assignments by subscription"

    # header
    ws1.cell(1, 1, u"{}".format(Config.vocabulary('member_pl')))
    ws1.column_dimensions['A'].width = 40
    ws1.cell(1, 2, u"{}".format(_('Arbeitseinsätze')))
    ws1.column_dimensions['B'].width = 17
    ws1.cell(1, 3, u"{}".format(_('{}-Grösse').format(Config.vocabulary('subscription'))))
    ws1.column_dimensions['C'].width = 17

    # data
    for row, subscription in enumerate(assignments_by_subscription(start_date, end_date), 2):
        ws1.cell(row, 1, ", ".join([member.get_name() for member in subscription['subscription'].members.all()]))
        ws1.cell(row, 2, subscription['assignments'])
        ws1.cell(row, 3, subscription['subscription'].totalsize)

    # Sheet 2: assignments per day
    ws2 = wb.create_sheet(title="assignments per day")

    # header
    ws2.cell(1, 1, u"{}".format(_('Datum')))
    ws2.column_dimensions['A'].width = 20
    ws2.cell(1, 2, u"{}".format(_('Arbeitseinsätze geleistet')))
    ws2.column_dimensions['B'].width = 17

    # data
    for row, assignment in enumerate(assignments_by_day(start_date, end_date), 2):
        ws2.cell(row, 1, assignment['day'])
        ws2.cell(row, 2, assignment['count'])

    # Sheet 3: slots by day
    ws3 = wb.create_sheet(title="slots per day")

    # header
    ws3.cell(1, 1, u"{}".format(_('Datum')))
    ws3.column_dimensions['A'].width = 20
    ws3.cell(1, 2, u"{}".format(_('Arbeitseinsätze ausgeschrieben')))
    ws3.column_dimensions['B'].width = 17

    # data
    for row, assignment in enumerate(slots_by_day(start_date, end_date), 2):
        ws3.cell(row, 1, assignment['day'])
        ws3.cell(row, 2, assignment['available'])

    wb.save(response)
    return response
