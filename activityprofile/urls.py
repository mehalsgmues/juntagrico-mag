"""mehalsgmues URL Configuration
"""
from django.contrib.auth.views import LoginView
from django.urls import path

from activityprofile.views import print_pdf, iframe

app_name = 'activityprofile'
urlpatterns = [
    path('print/<int:area_id>', print_pdf, name='print'),
    path('iframe/<int:area_id>', iframe, name='iframe'),
    path('login/', LoginView.as_view(template_name='activityprofile/login.html'), name='external-login'),
]
