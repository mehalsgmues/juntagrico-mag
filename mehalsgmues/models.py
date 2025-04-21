from django.db import models
from django.db.models.functions import Ceil
from django.utils.translation import gettext_lazy as _
from juntagrico.entity.jobs import Job
from juntagrico.queryset.subscription import SubscriptionQuerySet


class AccessInformation(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE,
                            verbose_name="Job")
    name = models.CharField(max_length=30)
    code = models.CharField(max_length=30)

    def __str__(self):
        return f'{self.job} - {self.name}'

    class Meta:
        verbose_name = _('Zugangsinfo')
        verbose_name_plural = _('Zugangsinfos')
        constraints = [
            models.UniqueConstraint(
                fields=['job', 'name'], name='unique job name')
        ]


# Override rounding of assignments
def my_rounding(number):
    return Ceil(number*2)/2


SubscriptionQuerySet._assignment_rounding = staticmethod(my_rounding)
