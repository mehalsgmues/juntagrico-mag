from django.contrib import admin

from juntagrico_proactive.entity.assignment_request import AssignmentRequest
from juntagrico_proactive.admins.assignment_request_admin import *


admin.site.register(AssignmentRequest, AssignmentRequestAdmin)
