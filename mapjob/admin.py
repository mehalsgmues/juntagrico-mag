from django.contrib import admin
from juntagrico.admins.job_admin import JobAdmin
from .models import MapJob


class MapJobAdmin(JobAdmin):
    def get_urls(self):
        # don't mess with the urls of the JobAdmin
        return super(JobAdmin, self).get_urls()


admin.site.register(MapJob, MapJobAdmin)
