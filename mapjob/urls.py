from django.urls import path

from . import views

app_name = 'mapjob'

urlpatterns = [
    path('jobs/', views.job_map, name='map'),
    path('jobs/<int:type_id>/', views.job_map_by_type, name='map_by_type'),
    path('list/', views.JobMapsListView.as_view(), name='list'),
    path('dashboard/', views.member_dashboard, name='member_dashboard'),

    path('job/<int:job_id>/set/progress/<str:progress>', views.set_job_progress, name='set_progress'),
    path('job/set/location', views.set_job_pickup_location, name='set_pickup_location'),
]
