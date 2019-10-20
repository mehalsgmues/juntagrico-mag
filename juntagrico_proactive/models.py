from django.db.models import signals

from juntagrico_proactive.entity.assignment_request import *

signals.pre_save.connect(AssignmentRequest.pre_save, sender=AssignmentRequest)
