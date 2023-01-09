from django.contrib import admin
from juntagrico.admins.job_admin import JobAdmin
from .models import MapJob


class MapJobAdmin(JobAdmin):
    pass


admin.site.register(MapJob, MapJobAdmin)
