from django.urls import path

from . import views

app_name = 'mapjob'

urlpatterns = [
    path('jobs/', views.job_map, name='map'),
    path('jobs/<int:type_id>/', views.job_map_by_type, name='map_by_type'),
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
]
