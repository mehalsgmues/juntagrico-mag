from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.views.generic import ListView

from juntagrico.entity.jobs import JobType

from mapjob.models import MapJob
from mapjob.utils import get_map_data

from . import member, admin  # noqa: F401
from .permissions import mapjob_change_required


def _render_job_map(request, jobs, job_type=None):
    return render(request, 'mapjob/job_map.html', {
        'jobs': jobs,
        'job_type': job_type,
        'map_job_data': get_map_data(jobs, extra_colors={MapJob.Progress.COMPLETE: "#0f0"})
    })


@mapjob_change_required
def job_map(request, days=60):
    return _render_job_map(request, MapJob.objects.recent(days).not_canceled())


@mapjob_change_required
def job_map_by_type(request, type_id):
    job_type = get_object_or_404(JobType, id=type_id)
    return _render_job_map(request, MapJob.objects.filter(type=type_id).not_canceled(), job_type)


@method_decorator(mapjob_change_required, name="dispatch")
class JobMapsListView(ListView):
    queryset = JobType.objects.filter(recuringjob__mapjob__isnull=False).distinct()
    template_name = "mapjob/mapjobtype_list.html"
