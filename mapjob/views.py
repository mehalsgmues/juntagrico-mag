from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from mapjob.models import MapJob
from mapjob.utils import get_map_job_data


@login_required
def job_map(request):
    jobs = MapJob.objects.all()
    return render(request, 'mapjob/job_map.html', {
        'jobs': jobs,
        'map_job_data': get_map_job_data(jobs, request.user.member)
    })
