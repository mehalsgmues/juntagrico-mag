import datetime


def next_start_date():
    # get next first of month that is at least 4 days away.
    start = datetime.date.today() + datetime.timedelta(days=4)
    if start.month < 4:
        return datetime.date(start.year, 4, 1)
    if start.month == 12:
        return datetime.date(start.year + 1, 1, 1)
    return datetime.date(start.year, start.month + 1, 1)
