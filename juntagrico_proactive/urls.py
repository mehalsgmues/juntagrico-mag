"""juntagrico_crowdfunding URL Configuration
"""
from django.urls import path
from juntagrico_proactive import views as proactive

urlpatterns = [
    path('proactive/assignment/request', proactive.request_assignment, name='proactive-request-assignment'),
    path('proactive/assignment/requested', proactive.request_assignment,
         {'sent': True}, name='proactive-assignment-requested'),
    path('proactive/assignment/delete/<int:request_id>/', proactive.delete_request_assignment,
         name='proactive-delete-assignment-request'),
    path('proactive/assignment/edit/<int:request_id>/', proactive.edit_request_assignment,
         name='proactive-edit-assignment-request'),
    path('proactive/assignment/list', proactive.list_assignment_requests,
         name='proactive-list-assignment-requests'),
    path('proactive/assignment/respond/<int:request_id>/', proactive.respond_assignment_request,
         name='proactive-respond-assignment-request'),
    path('proactive/assignment/confirm/<int:request_id>/', proactive.confirm_assignment_request,
         name='proactive-confirm-assignment-request'),
]
