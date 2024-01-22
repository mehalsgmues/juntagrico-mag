from django.db import models
from django.db.models import signals
from juntagrico.entity.jobs import RecuringJob
from django.utils.translation import gettext_lazy as _
from juntagrico.entity.location import Location
from juntagrico.util.signals import set_old_state


class PickupLocation(models.Model):
    location = models.OneToOneField(Location, on_delete=models.CASCADE)
    available_flyers = models.PositiveSmallIntegerField(_('Verfügbare Flyer'), default=0)

    def __str__(self):
        return f'{self.location.name} - {self.available_flyers} Flyer verfügbar'

    class Meta:
        verbose_name = _('Abholort')
        verbose_name_plural = _('Abholorte')


class MapJob(RecuringJob):
    class Progress(models.TextChoices):
        OPEN = 'OP', _('Offen')
        NEED_MORE = 'NM', _('Braucht mehr Flyer')
        PICKED_UP = 'PU', _('Abgeholt')
        DELIVERED = 'DL', _('Verteilt')
        RETURNED = 'RE', _('Erledigt')

    """
    Model that represents a job with a map area
    """
    geo_area = models.JSONField('geo_area')
    pickup_location = models.ForeignKey(PickupLocation, verbose_name=_('Abholort'),
                                        on_delete=models.SET_NULL, null=True, blank=True)
    progress = models.CharField(_('Fortschritt'), max_length=2, choices=Progress.choices, default=Progress.OPEN)
    used_flyers = models.PositiveSmallIntegerField(_('Verteilte Flyer'), default=0)

    def pickup_location_form(self):
        from .forms import PickupLocationForm
        return PickupLocationForm(instance=self)

    class Meta:
        verbose_name = _('Job mit Fläche')
        verbose_name_plural = _('Job mit Fläche')


signals.post_init.connect(set_old_state, sender=MapJob)
signals.post_save.connect(set_old_state, sender=MapJob)
