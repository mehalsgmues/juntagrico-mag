from django import template

from mapjob.models import MapJob
from mapjob.utils import get_map_data

register = template.Library()

@register.filter
def is_map_job(obj):
    return isinstance(obj, MapJob)


@register.simple_tag
def job_map_data():
    return get_map_data(MapJob.objects.active().undelivered().with_free_slots(), legend=False, urls=True)
