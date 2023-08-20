from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from juntagrico.entity.jobs import JobType

from mapjob.models import MapJob
from mapjob.utils import get_map_job_data


@login_required
def job_map(request):
    jobs = MapJob.objects.all()
    return render(request, 'mapjob/job_map.html', {
        'jobs': jobs,
        'map_job_data': get_map_job_data(jobs, request.user.member)
    })


@login_required
def job_map_by_type(request, type_id):
    jobs = MapJob.objects.filter(type=type_id)
    return render(request, 'mapjob/job_map.html', {
        'jobs': jobs,
        'map_job_data': get_map_job_data(jobs, request.user.member)
    })


@method_decorator(staff_member_required, name="dispatch")
class JobMapsListView(ListView):
    queryset = JobType.objects.filter(recuringjob__mapjob__isnull=False)
    template_name = "mapjob/mapjobtype_list.html"
