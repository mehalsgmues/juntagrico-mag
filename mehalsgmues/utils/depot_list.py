import datetime

from juntagrico.dao.depotdao import DepotDao
from juntagrico.dao.listmessagedao import ListMessageDao
from juntagrico.dao.subscriptionproductdao import SubscriptionProductDao
from juntagrico.entity.depot import Tour, Depot
from juntagrico.entity.subs import Subscription
from juntagrico.mailer import adminnotification
from juntagrico.util.pdf import render_to_pdf_storage

from mehalsgmues.utils.utils import get_delivery_dates_of_month


def mag_depot_list_generation(*args, days=0, force=False, **options):
    if not force:
        return

    date = datetime.date.today() + datetime.timedelta(days)

    # patch for delivery dates
    def delivery_dates(depot):
        return list(get_delivery_dates_of_month(depot.weekday - 1, date))

    Depot.delivery_dates = delivery_dates

    depot_dict = {
        'subscriptions': Subscription.objects.active_on(date).order_by('primary_member__first_name',
                                                                       'primary_member__last_name'),
        'products': SubscriptionProductDao.get_all_for_depot_list(),
        'depots': DepotDao.all_depots_for_list(),
        'date': date,
        'tours': Tour.objects.filter(visible_on_list=True),
        'messages': ListMessageDao.all_active()
    }

    render_to_pdf_storage('exports/depotlist.html',
                          depot_dict, 'depotlist.pdf')
    render_to_pdf_storage('exports/depot_overview.html',
                          depot_dict, 'depot_overview.pdf')
    render_to_pdf_storage('exports/amount_overview.html',
                          depot_dict, 'amount_overview.pdf')

    adminnotification.depot_list_generated()
