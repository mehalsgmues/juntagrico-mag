import calendar
import datetime
from collections import Counter
from math import floor

from dateutil.relativedelta import relativedelta
from django.db.models import Count, Sum, Q, functions
from django.utils import timezone
from juntagrico.dao.memberdao import MemberDao
from juntagrico.entity.jobs import Assignment, Job
from juntagrico.dao.subscriptiondao import SubscriptionDao
from juntagrico.entity.member import Member
from django.template.defaultfilters import date as date_filter
from juntagrico.entity.subs import Subscription


def jobs_in_activity_area(activity_area):
    return Job.objects.filter(
        Q(OneTimeJob___activityarea=activity_area) | Q(RecuringJob___type__activityarea=activity_area))


def get_trunc(name):
    return getattr(functions, 'Trunc' + name[0].upper() + name[1:])


def assignments_by(trunc, start_date, end_date, activity_area=None):
    trunc = get_trunc(trunc)
    return Assignment.objects.filter(job__time__range=(start_date, end_date),
                                     job__in=jobs_in_activity_area(activity_area)) \
        .annotate(**{trunc.kind: trunc('job__time')}) \
        .values(trunc.kind) \
        .annotate(count=Count('id')) \
        .order_by(trunc.kind)


def slots_by(trunc, start_date, end_date, activity_area=None):
    trunc = get_trunc(trunc)
    return jobs_in_activity_area(activity_area).filter(time__range=(start_date, end_date))\
        .annotate(**{trunc.kind: trunc('time')}) \
        .values(trunc.kind) \
        .annotate(available=Sum('slots'))\
        .order_by(trunc.kind)


def members_with_assignments(start_date, end_date, activty_area=None, members=None):
    members = members or MemberDao.all_members().filter(deactivation_date__gt=timezone.now().date())
    if isinstance(members, list):
        members = Member.objects.filter(pk__in=[m.pk for m in members])
    return members.annotate(assignments=Sum(
        'assignment__amount',
        filter=Q(assignment__job__time__range=(start_date, end_date)) & Q(
            assignment__job__in=jobs_in_activity_area(activty_area))
    )).filter(assignments__gt=0)


def assignments_by_subscription(start_date, end_date, activty_area=None):
    subscriptions_list = []
    for subscription in SubscriptionDao.all_active_subscritions().annotate(totalsize=Sum('parts__type__size__units')):
        assignments = 0
        for member in members_with_assignments(start_date, end_date, activty_area, members=subscription.recipients):
            if member.assignments:
                assignments += member.assignments

        subscriptions_list.append({
            'subscription': subscription,
            'assignments': assignments,
        })
    return subscriptions_list


class TemporalData:
    def __init__(self, trunc, start_date, end_date):
        self.trunc = trunc
        self.start_date = start_date
        self.end_date = end_date

    def date_to_number(self, date):
        if self.trunc == 'day':
            return date.timetuple().tm_yday
        if self.trunc == 'week':
            return date.isocalendar()[1]
        if self.trunc == 'month':
            return date.month

    def trunc_adjective(self):
        if self.trunc == 'day':
            return 'täglich'
        if self.trunc == 'week':
            return 'wöchentlich'
        if self.trunc == 'month':
            return 'monatlich'

    def date_to_label(self, date):
        if self.trunc == 'day':
            return date.strftime('%d.%m')
        if self.trunc == 'week':
            return f'KW{date.isocalendar()[1]}'
        if self.trunc == 'month':
            return date_filter(date, 'F')

    def trunc_per_year(self, date):
        if self.trunc == 'day':
            return 366 if calendar.isleap(date.year) else 365
        if self.trunc == 'week':
            return datetime.date(date.year, 12, 28).isocalendar()[1]
        if self.trunc == 'month':
            return 12

    def increment_by_trunc(self, interval=1):
        if self.trunc == 'day':
            return datetime.timedelta(interval)
        if self.trunc == 'week':
            return datetime.timedelta(weeks=interval)
        if self.trunc == 'month':
            return relativedelta(months=interval)

    def data_to_dict(self, data_function, value='count'):
        result = {}
        last_date = self.start_date
        for data_point in data_function(self.trunc, self.start_date, self.end_date):
            date = data_point[self.trunc].date()
            # fill dates without data
            while last_date < date:
                result[last_date] = 0
                last_date += self.increment_by_trunc()
            result[date] = data_point[value]
            last_date += self.increment_by_trunc()
        # fill until end_date
        while last_date < self.end_date:
            result[last_date] = 0
            last_date += self.increment_by_trunc()
        return result


def get_assignment_progress(start_date, end_date, normalize=False):
    progresses = Subscription.objects.exclude(deactivation_date__lt=start_date).annotate_assignments_progress(start_date, end_date) \
        .exclude(required_assignments=0).values('assignments_progress', 'cancellation_date')

    end = end_date + datetime.timedelta(1)

    t = Counter((floor(min(p['assignments_progress'], 100) / 20) + 6 * ((p['cancellation_date'] or end) < end) for p in progresses))
    norm = len(progresses) / 100 if normalize else 1
    data = [t[k] / norm for k in range(0, 12)]
    return {'active': data[:6], 'cancelled': data[6:], 'year': start_date.year}
