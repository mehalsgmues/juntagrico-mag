from django import template

from mapjob.models import MapJob

register = template.Library()

@register.filter
def is_map_job(obj):
    return isinstance(obj, MapJob)
