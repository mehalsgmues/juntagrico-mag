from django.db import models
from django.db.models import Count, Q, F


class MapJobQueryset(models.QuerySet):
    def of_member(self, member):
        return self.filter(assignment__member=member).distinct()

    def with_free_slots(self):
        return self.annotate(occupied_count=Count('assignment')).filter(
            Q(infinite_slots=True) | Q(occupied_count__lt=F('slots'))
        )

    def need_pickup(self):
        return self.filter(progress__in=[self.model.Progress.OPEN, self.model.Progress.NEED_MORE])

    def delivering(self):
        return self.filter(progress__in=[self.model.Progress.PICKED_UP])
