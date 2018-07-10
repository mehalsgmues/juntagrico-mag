from django import template
from juntagrico.entity.jobs import RecuringJob

register = template.Library()

@register.filter
def isRecuring(job):
    print(type(job))
    return type(job) is RecuringJob
