from django import template
from django.utils.html import json_script

from mapjob.models import MapJob
from mapjob.utils import get_map_job_data

register = template.Library()

@register.filter
def is_map_job(obj):
    return isinstance(obj, MapJob)


@register.simple_tag
def job_map_data(member):
    return json_script(get_map_job_data(MapJob.objects.all(), member), 'map_job_data')
