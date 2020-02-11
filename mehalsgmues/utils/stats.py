from django.db.models.functions import TruncDay
from django.db.models import Count, Sum, Q
from juntagrico.dao.memberdao import MemberDao
from juntagrico.entity.jobs import Assignment, Job
from juntagrico.dao.subscriptiondao import SubscriptionDao


def jobs_in_activity_area(activity_area):
    return Job.objects.filter(Q(OneTimeJob___activityarea=activity_area)
                              | Q(RecuringJob___type__activityarea=activity_area))


def assignments_by_day(start_date, end_date, activity_area=None):
    return Assignment.objects.filter(job__time__range=(start_date, end_date),
                                     job__in=jobs_in_activity_area(activity_area))\
        .annotate(day=TruncDay('job__time'))\
        .values('day')\
        .annotate(count=Count('id'))


def slots_by_day(start_date, end_date, activity_area=None):
    return jobs_in_activity_area(activity_area).filter(time__range=(start_date, end_date))\
        .annotate(day=TruncDay('time')) \
        .values('day') \
        .annotate(available=Sum('slots'))


def members_with_assignments(start_date, end_date, activty_area=None, members=None):
    members = members or MemberDao.all_members().filter(inactive=False)
    return members.annotate(assignments=Sum(
        'assignment__amount',
        filter=Q(assignment__job__time__range=(start_date, end_date)) & Q(assignment__job__in=
                                                                          jobs_in_activity_area(activty_area))
    )).filter(assignments__gt=0)


def assignments_by_subscription(start_date, end_date, activty_area=None):
    subscriptions_list = []
    for subscription in SubscriptionDao.all_active_subscritions().annotate(totalsize=Sum('types__size__units')):
        assignments = 0
        for member in members_with_assignments(start_date, end_date, activty_area, members=subscription.members):
            if member.assignments:
                assignments += member.assignments

        subscriptions_list.append({
            'subscription': subscription,
            'assignments': assignments,
        })
    return subscriptions_list
