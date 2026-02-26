from juntagrico.entity.depot import Depot
from juntagrico.mailer import adminnotification
from juntagrico.util.pdf import render_to_pdf_storage

from mehalsgmues.utils.utils import get_delivery_dates_of_month


def mag_depot_list_generation(context):
    # patch for delivery dates
    def delivery_dates(depot):
        return list(get_delivery_dates_of_month(depot.weekday - 1, context['date']))

    Depot.delivery_dates = delivery_dates

    depot_dict = context | {
        'count_sizes': sum(p.sizes.on_depot_list().count() for p in context['products']),
    }

    render_to_pdf_storage('exports/depotlist.html',
                          depot_dict, 'depotlist.pdf')
    render_to_pdf_storage('exports/depot_overview.html',
                          depot_dict, 'depot_overview.pdf')
    render_to_pdf_storage('exports/amount_overview.html',
                          depot_dict, 'amount_overview.pdf')

    adminnotification.depot_list_generated()
