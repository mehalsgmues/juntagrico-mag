from django.contrib.admin.views.decorators import staff_member_required
from django.core.management import call_command
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from juntagrico.dao.subscriptiondao import SubscriptionDao
from juntagrico.entity.depot import Depot
from juntagrico.entity.subs import Subscription
from juntagrico.mailer import membernotification
from juntagrico.util import return_to_previous_location
from juntagrico.util.views_admin import subscription_management_list

from mehalsgmues.utils.utils import get_delivery_dates_of_month


@staff_member_required
def list_mgmt(request, success=False):
    return render(request, 'mag/list_mgmt.html', {'success': success})


@staff_member_required
def list_generate(request, future=False):
    def delivery_dates(depot):
        return list(get_delivery_dates_of_month(depot.weekday - 1, int(request.GET.get('month', 0))))
    Depot.delivery_dates = delivery_dates
    call_command('generate_depot_list', force=True, future=future)
    return redirect(reverse('lists-mgmt-success'))


@staff_member_required
def depot_changes(request):
    render_dict = {'change_date_disabled': True}
    return subscription_management_list(SubscriptionDao.subscritions_with_future_depots(), render_dict,
                                        'mag/management_lists/depot_changelist.html', request)


@staff_member_required
def depot_change_confirm(request, subscription_id):
    # Cheap copy of juntagrico util/subs.py activate_future_depots
    sub = get_object_or_404(Subscription, id=subscription_id)
    sub.depot = sub.future_depot
    sub.future_depot = None
    sub.save()
    emails = []
    for member in sub.recipients:
        emails.append(member.email)
    membernotification.depot_changed(emails, sub.depot)
    return return_to_previous_location(request)
