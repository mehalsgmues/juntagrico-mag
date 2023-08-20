from django.urls import path

from mapjob.views import job_map, job_map_by_type, JobMapsListView

app_name = 'mapjob'

urlpatterns = [
    path('jobs', job_map, name='map'),
    path('jobs/<int:type_id>', job_map_by_type, name='map_by_type'),
    path('list', JobMapsListView.as_view(), name='list')
]
