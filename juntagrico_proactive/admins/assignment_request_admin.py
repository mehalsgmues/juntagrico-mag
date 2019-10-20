from juntagrico.admins import BaseAdmin


class AssignmentRequestAdmin(BaseAdmin):
    list_display = ['member', 'amount', 'job_time', 'duration', 'activityarea',
                    'location', 'request_date', 'approver', 'status', ]
    readonly_fields = ('assignment',)
