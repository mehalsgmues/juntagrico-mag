"""mehalsgmues URL Configuration
"""
from django.urls import path

from mapjob.views import job_map

app_name = 'mapjob'
urlpatterns = [
    path('jmj/map', job_map, name='map'),
]
