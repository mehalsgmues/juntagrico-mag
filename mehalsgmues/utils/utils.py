from datetime import datetime, timedelta


def date_from_get(request, name, default, date_format="%Y-%m-%d"):
    date = request.GET.get(name, None)
    if date is not None:
        return datetime.strptime(date, date_format)
    return default


def get_delivery_dates_of_month(delivery_weekday, relative_month):
    today = datetime.today()
    # get dates of next month if this month is half over.
    month = today.month + int(today.day > 15) + relative_month
    date = datetime(today.year, month, 1)
    next_delivery = date + timedelta(days=(delivery_weekday - 1 - date.weekday()) % 7)
    yield next_delivery
    while True:
        next_delivery = next_delivery + timedelta(days=7)
        if next_delivery.month == month:
            yield next_delivery
        else:
            break
