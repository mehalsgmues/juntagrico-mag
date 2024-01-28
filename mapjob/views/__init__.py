from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import ListView

from juntagrico.entity.jobs import JobType

from mapjob.models import MapJob
from mapjob.utils import get_map_data

from . import member  # noqa: F401


@staff_member_required
def job_map(request, jobs=None, days=60):
    jobs = jobs or MapJob.objects.recent(days)
    return render(request, 'mapjob/job_map.html', {
        'jobs': jobs,
        'map_job_data': get_map_data(jobs, extra_colors={MapJob.Progress.COMPLETE: "#0f0"})
    })


@staff_member_required
def job_map_by_type(request, type_id):
    return job_map(request, MapJob.objects.filter(type=type_id))


@method_decorator(staff_member_required, name="dispatch")
class JobMapsListView(ListView):
    queryset = JobType.objects.filter(recuringjob__mapjob__isnull=False).distinct()
    template_name = "mapjob/mapjobtype_list.html"
