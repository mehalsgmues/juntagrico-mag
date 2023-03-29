import datetime

from dateutil.relativedelta import relativedelta
from juntagrico.dao.depotdao import DepotDao
from juntagrico.dao.listmessagedao import ListMessageDao
from juntagrico.dao.subscriptionproductdao import SubscriptionProductDao
from juntagrico.entity.subs import Subscription
from juntagrico.mailer import adminnotification
from juntagrico.util.pdf import render_to_pdf_storage
from juntagrico.util.temporal import weekdays


def mag_depot_list_generation(*args, **options):
    if not options['force']:
        return

    date = datetime.date.today() + relativedelta(months=1 if options['future'] else 0)

    print(date)

    depot_dict = {
        'subscriptions': Subscription.objects.filter(activation_date__lte=date).exclude(deactivation_date__lt=date).order_by('primary_member__first_name', 'primary_member__last_name'),
        'products': SubscriptionProductDao.get_all_for_depot_list(),
        'depots': DepotDao.all_depots_for_list(),

        'weekdays': {weekdays[weekday['weekday']]: weekday['weekday'] for weekday in
                     DepotDao.distinct_weekdays_for_depot_list()},
        'messages': ListMessageDao.all_active()
    }

    render_to_pdf_storage('exports/depotlist.html',
                          depot_dict, 'depotlist.pdf')
    render_to_pdf_storage('exports/depot_overview.html',
                          depot_dict, 'depot_overview.pdf')
    render_to_pdf_storage('exports/amount_overview.html',
                          depot_dict, 'amount_overview.pdf')

    adminnotification.depot_list_generated()
