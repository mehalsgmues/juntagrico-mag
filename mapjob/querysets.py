from datetime import timedelta

from django.db import models
from django.db.models import Count, Q, F
from django.utils import timezone


class MapJobQueryset(models.QuerySet):
    def of_member(self, member):
        return self.filter(assignment__member=member).distinct()

    def with_free_slots(self):
        return self.annotate(occupied_count=Count('assignment')).filter(
            Q(infinite_slots=True) | Q(occupied_count__lt=F('slots'))
        )

    def recent(self, days=0):
        return self.filter(time__gte=timezone.now() - timedelta(days=days))

    def active(self):
        return self.exclude(progress=self.model.Progress.COMPLETE)

    def need_pickup(self):
        return self.filter(progress__in=[self.model.Progress.OPEN, self.model.Progress.NEED_MORE])

    def picked_up(self):
        return self.filter(progress__in=[self.model.Progress.PICKED_UP, self.model.Progress.DELIVERED])

    def undelivered(self):
        return self.exclude(progress=self.model.Progress.DELIVERED)

    def completed(self):
        return self.filter(progress=self.model.Progress.COMPLETE)
