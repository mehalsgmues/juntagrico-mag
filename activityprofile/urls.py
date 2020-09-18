"""mehalsgmues URL Configuration
"""
from django.urls import path

from activityprofile.views import print_pdf, iframe

app_name = 'activityprofile'
urlpatterns = [
    path('print/<int:area_id>', print_pdf, name='print'),
    path('iframe/<int:area_id>', iframe, name='iframe'),
]
