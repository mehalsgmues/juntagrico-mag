from django.contrib.auth.decorators import login_required
from django.utils.safestring import mark_safe
from juntagrico.dao.extrasubscriptioncategorydao import ExtraSubscriptionCategoryDao
from juntagrico.dao.memberdao import MemberDao
from juntagrico.dao.subscriptiondao import SubscriptionDao
from juntagrico.dao.subscriptionproductdao import SubscriptionProductDao
from juntagrico.dao.subscriptiontypedao import SubscriptionTypeDao
from juntagrico.entity.jobs import ActivityArea
from openpyxl import Workbook

import base64
import hmac
import hashlib
from urllib import parse
from django.conf import settings


from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

from juntagrico.models import Member, Subscription

from juntagrico.dao.depotdao import DepotDao
from juntagrico.dao.listmessagedao import ListMessageDao
from juntagrico.dao.subscriptionsizedao import SubscriptionSizeDao
from juntagrico.util.pdf import render_to_pdf_http
from juntagrico.util.temporal import weekdays, start_of_business_year, end_of_business_year
from juntagrico.config import Config
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from openpyxl.utils import get_column_letter

from mehalsgmues.utils.stats import assignments_by_subscription, assignments_by_day, slots_by_day, \
    members_with_assignments
from mehalsgmues.utils.utils import date_from_get, get_delivery_dates_of_month


# API
@staff_member_required
def api_emaillist(request):
    """prints comma separated list of member emails"""
    # get emails
    return HttpResponse(', '.join(Member.objects.filter(inactive=False).values_list('email', flat=True)))


@login_required
def nextcloud_profile(request):
    member = request.user.member
    membergroups = request.user.groups.values_list('name', flat=True)
    grouplist = list(membergroups)
    response = JsonResponse({'id': member.id,
                             'email': member.email,
                             'firstName': member.first_name,
                             'lastName': member.last_name,
                             'displayName': member.first_name + " " + member.last_name,
                             'roles': grouplist})
    return response


# pdf
def generate_pdf_dict():
    return {
        'subscriptions': SubscriptionDao.all_active_subscritions(),
        'products': SubscriptionProductDao.get_all(),
        'extra_sub_categories': ExtraSubscriptionCategoryDao.categories_for_depot_list_ordered(),
        'depots': DepotDao.all_depots_order_by_code(),
        'weekdays': {weekdays[weekday['weekday']]: weekday['weekday'] for weekday in
                     DepotDao.distinct_weekdays()},
        'messages': ListMessageDao.all_active()
    }


def other_recipients_names_w_linebreaks(self):
    members = self.recipients.exclude(email=self.primary_member.email)
    members = [str(member) for member in members]
    return mark_safe('<br>'.join([', '.join(members[x:x+6]) for x in range(0, len(members), 6)]))


@staff_member_required
def depot_list(request):
    depot_dict = generate_pdf_dict()
    for depot in depot_dict['depots']:
        depot.delivery_dates = list(get_delivery_dates_of_month(depot.weekday, int(request.GET.get('month', 0))))
    Subscription.other_recipients_names_w_linebreaks = other_recipients_names_w_linebreaks
    return render_to_pdf_http('exports/depotlist.html', depot_dict, 'depotlist.pdf')


@staff_member_required
def depot_overview(request):
    return render_to_pdf_http('exports/depot_overview.html', generate_pdf_dict(), 'depot_overview.pdf')


@staff_member_required
def amount_overview(request):
    return render_to_pdf_http('exports/amount_overview.html', generate_pdf_dict(), 'amount_overview.pdf')


@staff_member_required
def stats(request):
    activity_area = ActivityArea.objects.filter(pk=request.GET.get('activity_area', None)).first()

    start_date = date_from_get(request, 'start_date', start_of_business_year())
    end_date = date_from_get(request, 'end_date', end_of_business_year())

    filename = '{}_{}_{}stats.xlsx'.format(
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d'),
        str(activity_area.pk) + '_' if activity_area else ''
    )
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
    for row, subscription in enumerate(assignments_by_subscription(start_date, end_date, activity_area), 2):
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
    for row, assignment in enumerate(assignments_by_day(start_date, end_date, activity_area), 2):
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
    for row, assignment in enumerate(slots_by_day(start_date, end_date, activity_area), 2):
        ws3.cell(row, 1, assignment['day'])
        ws3.cell(row, 2, assignment['available'])

    # Sheet 4: assignments per member
    ws4 = wb.create_sheet(title="assignments per member")

    # header
    ws4.cell(1, 1, u"{}".format(Config.vocabulary('member')))
    ws4.column_dimensions['A'].width = 40
    ws4.cell(1, 2, u"{}".format(_('Arbeitseinsätze')))
    ws4.column_dimensions['B'].width = 17

    # data
    members = members_with_assignments(start_date, end_date, activity_area)
    for row, member in enumerate(members, 2):
        ws4.cell(row, 1, u"{}".format(member))
        ws4.cell(row, 2, member.assignments)

    wb.save(response)
    return response


@staff_member_required
def excel_export_subscriptions(request):
    filename = '{}_{}.xlsx'.format(Config.vocabulary('subscription_pl'), timezone.now().date())
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=' + filename
    wb = Workbook()

    # Sheet 1: Subscriptions with prices
    ws1 = wb.active
    ws1.title = Config.vocabulary('subscription_pl')

    # header
    ws1.cell(1, 1, u"{}".format(Config.vocabulary('member_pl')))
    ws1.column_dimensions['A'].width = 40
    ws1.cell(1, 2, u"{}".format(_('E-Mail')))
    ws1.column_dimensions['B'].width = 30
    ws1.cell(1, 3, u"{}".format(_('Gesamtpreis [{}]').format(Config.currency())))
    ws1.column_dimensions['C'].width = 17
    for column, subs_type in enumerate(SubscriptionTypeDao.get_all(), 4):
        ws1.cell(1, column, u"EAT {}".format(subs_type.price))
        ws1.column_dimensions[get_column_letter(column)].width = 17

    # data
    for row, subscription in enumerate(SubscriptionDao.all_active_subscritions(), 2):
        ws1.cell(row, 1, ", ".join([member.get_name() for member in subscription.members.all()]))
        ws1.cell(row, 2, subscription.primary_member.email)
        ws1.cell(row, 3, subscription.price)
        for column, subs_type in enumerate(SubscriptionTypeDao.get_all(), 4):
            ws1.cell(row, column, subscription.types.filter(id=subs_type.id).count())

    ws1.freeze_panes = ws1['A2']
    wb.save(response)
    return response


@login_required
def sso(request):
    payload = request.GET.get('sso')
    signature = request.GET.get('sig')

    if payload is None or signature is None:
        raise Exception('No SSO payload or signature. Please contact support if this problem persists.')

    # Validate the payload
    try:
        payload = bytes(parse.unquote(payload), encoding='utf-8')
        decoded = base64.decodebytes(payload).decode('utf-8')
        assert 'nonce' in decoded
        assert len(payload) > 0
    except AssertionError:
        raise Exception('Invalid payload. Please contact support if this problem persists.')

    key = bytes(settings.DISCOURSE_SSO_SECRET, encoding='utf-8')  # must not be unicode
    h = hmac.new(key, payload, digestmod=hashlib.sha256)
    this_signature = h.hexdigest()

    if not hmac.compare_digest(this_signature, signature):
        raise Exception('Invalid payload. Please contact support if this problem persists.')

    # Build the return payload
    qs = parse.parse_qs(decoded)
    params = {
        'nonce': qs['nonce'][0],
        'email': request.user.member.email,
        'external_id': request.user.id,
        'username': '%s.%s' % (request.user.member.first_name.lower(), request.user.member.last_name.lower()),
        'name': request.user.member.get_name(),
    }

    return_payload = base64.encodebytes(bytes(parse.urlencode(params), 'utf-8'))
    h = hmac.new(key, return_payload, digestmod=hashlib.sha256)
    query_string = parse.urlencode({'sso': return_payload, 'sig': h.hexdigest()})

    # Redirect back to Discourse
    url = '%s/session/sso_login' % settings.DISCOURSE_BASE_URL
    return HttpResponseRedirect('%s?%s' % (url, query_string))