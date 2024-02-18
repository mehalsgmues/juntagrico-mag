from datetime import date

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from juntagrico.config import Config
from juntagrico.dao.subscriptiondao import SubscriptionDao
from juntagrico.dao.subscriptiontypedao import SubscriptionTypeDao
from juntagrico.entity.member import Member
from juntagrico.entity.share import Share
from juntagrico.util.views_admin import subscription_management_list
from juntagrico.view_decorators import any_permission_required
from openpyxl import Workbook
from openpyxl.utils import get_column_letter

from mehalsgmues.utils.utils import forum_notifications


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
        ws1.cell(row, 1, ", ".join([member.get_name() for member in subscription.recipients]))
        ws1.cell(row, 2, subscription.primary_member.email)
        ws1.cell(row, 3, subscription.price)
        for column, subs_type in enumerate(SubscriptionTypeDao.get_all(), 4):
            ws1.cell(row, column, subscription.active_parts.filter(type__id=subs_type.id).count())

    ws1.freeze_panes = ws1['A2']
    wb.save(response)
    return response


@login_required
def ajax_notifications(request):
    notifications = forum_notifications(request.user)
    if notifications is None:
        notifications = u"\u00A0"
    return HttpResponse(notifications)


@permission_required('juntagrico.view_share')
def share_unpaidlist(request):
    render_dict = {'change_date_disabled': True}
    return subscription_management_list(Share.objects.filter(paid_date__isnull=True).order_by('member'), render_dict,
                                        'mag/management_lists/share_unpaidlist.html', request)


@any_permission_required('juntagrico.can_filter_members', 'juntagrico.change_member')
def filters_active(request):
    renderdict = {
        'members': Member.objects.exclude(share=None).filter(Q(share__payback_date__gte=date.today()) | Q(share__payback_date__isnull=True)).distinct(),
        'title': 'Alle Mitglieder'
    }
    return render(request, 'management_lists/members.html', renderdict)
