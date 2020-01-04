from django.db.models.functions import TruncDay
from django.db.models import Count, Sum, Q
from juntagrico.entity.jobs import Assignment, Job
from juntagrico.dao.subscriptiondao import SubscriptionDao


def assignments_by_day(start_date, end_date):
    return Assignment.objects.filter(job__time__range=(start_date, end_date))\
        .annotate(day=TruncDay('job__time'))\
        .values('day')\
        .annotate(count=Count('id'))


def slots_by_day(start_date, end_date):
    return Job.objects.filter(time__range=(start_date, end_date))\
        .annotate(day=TruncDay('time')) \
        .values('day') \
        .annotate(available=Sum('slots'))


def assignments_by_subscription(start_date, end_date):
    subscriptions_list = []
    for subscription in SubscriptionDao.all_active_subscritions().annotate(totalsize=Sum('types__size__units')):
        assignments = 0
        for member in subscription.members.annotate(
                assignments=Sum('assignment__amount', filter=Q(assignment__job__time__range=(start_date, end_date)))):
            if member.assignments:
                assignments += member.assignments

        subscriptions_list.append({
            'subscription': subscription,
            'assignments': assignments,
        })
    return subscriptions_list
