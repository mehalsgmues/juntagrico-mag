from django.db import models
from django.db.models import signals
from juntagrico.config import Config
from juntagrico.entity.jobs import RecuringJob, Assignment
from django.utils.translation import gettext_lazy as _
from juntagrico.entity.location import Location
from juntagrico.util.signals import set_old_state

from mapjob.querysets import MapJobQueryset


class PickupLocation(models.Model):
    location = models.OneToOneField(Location, on_delete=models.CASCADE)
    available_flyers = models.IntegerField(_('Verfügbare Flyer'), default=0)

    def __str__(self):
        if self.available_flyers <= 0 :
            available = _('Keine Flyer verfügbar')
        else:
            available = _('{} Flyer verfügbar').format(self.available_flyers)
        return f'{self.location.name} - ' + available

    class Meta:
        verbose_name = _('Abholort')
        verbose_name_plural = _('Abholorte')


class MapJob(RecuringJob):
    class Progress(models.TextChoices):
        OPEN = 'OP', _('Offen')
        NEED_MORE = 'NM', _('Braucht mehr Flyer')
        PICKED_UP = 'PU', _('Abgeholt')
        DELIVERED = 'DL', _('Verteilt')
        COMPLETE = 'CO', _('Erledigt')

    """
    Model that represents a job with a map area
    """
    geo_area = models.JSONField('geo_area')
    pickup_location = models.ForeignKey(PickupLocation, verbose_name=_('Abholort'),
                                        on_delete=models.SET_NULL, null=True, blank=True)
    progress = models.CharField(_('Fortschritt'), max_length=2, choices=Progress.choices, default=Progress.OPEN)
    used_flyers = models.PositiveSmallIntegerField(_('Verteilte Flyer'), default=0)

    objects = MapJobQueryset.as_manager()

    def pickup_location_form(self):
        from .forms import PickupLocationForm
        return PickupLocationForm(instance=self, prefix=self.id)

    def assign(self, member):
        # This should be a functon in juntagrico
        if self.free_slots > 0:
            amount = self.multiplier
            if Config.assignment_unit() == 'HOURS':
                amount *= self.duration
            return Assignment.objects.create(member=member, job=self, amount=amount)

    def __str__(self):
        try:
            return self.geo_area['properties']['name']
        except (TypeError, KeyError):
            return super().__str__()

    class Meta:
        verbose_name = _('Job mit Fläche')
        verbose_name_plural = _('Job mit Fläche')


signals.post_init.connect(set_old_state, sender=MapJob)
signals.post_save.connect(set_old_state, sender=MapJob)
