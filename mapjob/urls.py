from django.urls import path

from mapjob.views import job_map

app_name = 'mapjob'
urlpatterns = [
    path('jobs', job_map, name='map'),
]
