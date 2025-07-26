from django.urls import path

from . import views

urlpatterns = [
    path('mail/queue', views.mail_queue, name='mail-queue'),
    # override email sent result page
    path('mail/queue/<int:numsent>/', views.mail_queue, name='mail-result'),
]
