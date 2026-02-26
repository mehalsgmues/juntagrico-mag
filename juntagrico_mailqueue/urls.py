from django.urls import path

from . import views

urlpatterns = [
    path('mail/queue', views.mail_queue, name='mail-queue'),
    # override sent page
    path('email/sent', views.sent, name='email-sent'),
]
