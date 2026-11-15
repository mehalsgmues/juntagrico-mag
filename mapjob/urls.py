from django.urls import path

from . import views
from .views import edit

app_name = 'mapjob'

urlpatterns = [
    path('jobs/', views.job_map, name='map'),
    path('jobs/<int:type_id>/', views.job_map_by_type, name='map_by_type'),
    path('jobs/<int:type_id>/edit/', edit.edit_map_by_type, name='edit_map_by_type'),
    path('list/', views.JobMapsListView.as_view(), name='list'),

    # member views
    path('dashboard/', views.member.delivery_dashboard, name='member_dashboard'),
    path('dashboard/available_areas/', views.member.available_areas, name='available_areas'),

    # member actions
    path('job/<int:job_id>/register/', views.member.actions.register, name='register'),
    path('job/<int:job_id>/set/progress/<str:progress>/', views.member.actions.set_job_progress, name='set_progress'),
    path('job/<int:job_id>/set/location/', views.member.actions.set_job_pickup_location, name='set_job_pickup_location'),
    path('job/all/set/location/', views.member.actions.set_job_pickup_location, name='set_all_pickup_location'),
    path('pickup/', views.member.actions.pickup, name='pickup'),
    path('return/', views.member.actions.return_remaining, name='return'),
    path('complete/all/', views.member.actions.complete, name='complete'),

    # admin
    path('admin/mapjob/import/', views.admin.import_csv, name='import'),
    path('admin/mapjob/select_entries/', views.admin.select_entries, name='select_entries'),

    # API
    path('api/job/<int:job_id>/save_geo_area/', edit.save_geo_area, name='save_geo_area'),
    path('api/job/create/', edit.create_map_job, name='create_map_job'),
    path('api/job/<int:job_id>/info/', edit.get_map_job_info, name='get_map_job_info'),
    path('api/job/<int:job_id>/delete/', edit.delete_map_job, name='delete_map_job'),
    path('api/job/<int:job_id>/cancel/', edit.cancel_map_job, name='cancel_map_job'),
]
