from django.db import models
from django.db.models import signals
from juntagrico.entity.jobs import RecuringJob
from django.utils.translation import gettext as _
from juntagrico.util.signals import set_old_state


class MapJob(RecuringJob):
    """
    Model that represents a job with a map area
    """
    geo_area = models.JSONField('geo_area')

    class Meta:
        verbose_name = _('Job mit Fläche')
        verbose_name_plural = _('Job mit Fläche')


signals.post_init.connect(set_old_state, sender=MapJob)
signals.post_save.connect(set_old_state, sender=MapJob)
