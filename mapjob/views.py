from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.views.generic import ListView
from django.utils.translation import gettext as _

from juntagrico.entity.jobs import JobType
from juntagrico.util import return_to_previous_location

from mapjob.forms import PickupLocationForm
from mapjob.models import MapJob
from mapjob.utils import get_map_job_data


@login_required
def job_map(request, jobs=None):
    jobs = jobs or MapJob.objects.all()
    return render(request, 'mapjob/job_map.html', {
        'jobs': jobs,
        'has_jobs': jobs.filter(assignment__member=request.user.member).exists(),
        'map_job_data': get_map_job_data(jobs, request.user.member)
    })


@login_required
def job_map_by_type(request, type_id):
    return job_map(request, MapJob.objects.filter(type=type_id))


@method_decorator(staff_member_required, name="dispatch")
class JobMapsListView(ListView):
    queryset = JobType.objects.filter(recuringjob__mapjob__isnull=False).distinct()
    template_name = "mapjob/mapjobtype_list.html"


@login_required
def member_dashboard(request):
    jobs = MapJob.objects.filter(assignment__member=request.user.member).distinct()

    map_job_data = []
    for map_job in jobs:
        geo = map_job.geo_area
        geo['properties'].update({
            'status': map_job.progress
        })
        map_job_data.append(geo)

    colors = {
        MapJob.Progress.OPEN: "#ff0000",
        MapJob.Progress.NEED_MORE: "#ff8800",
        MapJob.Progress.PICKED_UP: "#ffff00",
        MapJob.Progress.DELIVERED: "#88ff00",
        MapJob.Progress.RETURNED: "#00ff00",
    }
    legend = {
        p: [p.label, colors[p]] for p in MapJob.Progress
    }
    legend["default"] = [_("Unbekannt"), "#000000"]

    return render(request, 'mapjob/dashboard.html', {
        'jobs': jobs,
        'map_job_data': {
            'data': map_job_data,
            'legend': legend
        },
    })


@login_required
def set_job_progress(request, job_id, progress):
    job = get_object_or_404(MapJob, id=job_id, assignment__member=request.user.member)
    job.progress = progress
    job.save()
    return return_to_previous_location(request)


@login_required
def set_job_pickup_location(request):
    if request.method == 'POST':
        job = get_object_or_404(MapJob, id=request.POST['id'], assignment__member=request.user.member)
        form = PickupLocationForm(instance=job, data=request.POST)
        if form.is_valid():
            messages.success(request, _("Gewünschter Abholort wurde geändert."))
            form.save()
        else:
            for field, error in form.errors.items():
                messages.error(request, mark_safe(f'{field}: {error}'), extra_tags='danger')
    return return_to_previous_location(request)
