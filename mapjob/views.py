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

from mapjob.forms import PickupLocationForm, AllPickupLocationForm, PickupForm
from mapjob.models import MapJob
from mapjob.utils import get_map_job_data


@login_required
def job_map(request, jobs=None):
    jobs = jobs or MapJob.objects.all()
    return render(request, 'mapjob/job_map.html', {
        'jobs': jobs,
        'has_jobs': jobs.of_member(request.user.member).exists(),
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
    member = request.user.member
    # jobs of member
    own_jobs = MapJob.objects.of_member(member)

    own_job_geo = []
    for map_job in own_jobs:
        geo = map_job.geo_area
        geo['properties'].update({
            'status': map_job.progress,
        })
        own_job_geo.append(geo)

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

    # available map jobs
    available_jobs = MapJob.objects.with_free_slots()

    available_job_geo = []
    for map_job in available_jobs:
        geo = map_job.geo_area
        geo['properties'].update({
            'color': "#ff0000",
        })
        available_job_geo.append(geo)

    # pickup form
    pickup_form = None
    pickup_location_form = None
    pickup_jobs = own_jobs.need_pickup()
    if pickup_jobs:
        pickup_form = PickupForm(pickup_jobs)
        pickup_location_form = AllPickupLocationForm(initial={'pickup_location': pickup_jobs.first().pickup_location})

    # return form
    return_form = None
    return_job = own_jobs.filter(progress__in=[MapJob.Progress.PICKED_UP, MapJob.Progress.DELIVERED]).first()
    if return_job:
        return_form = AllPickupLocationForm(initial={'pickup_location': return_job.pickup_location})

    return render(request, 'mapjob/dashboard.html', {
        'own_jobs': own_jobs,
        'available_jobs': available_jobs,
        'map_job_data': {
            'reserved': {
                'data': own_job_geo,
                'legend': legend
            },
            'available': {
                'data': available_job_geo
            }
        },
        'pickup_form': pickup_form,
        'pickup_location_form': pickup_location_form,
        'return_form': return_form,
    })


@login_required
def set_job_progress(request, job_id, progress):
    job = get_object_or_404(MapJob.objects.of_member(request.user.member), id=job_id)
    job.progress = progress
    job.save()
    return return_to_previous_location(request)


@login_required
def pickup(request):
    if request.method == 'POST':
        form = PickupForm(MapJob.objects.of_member(request.user.member).need_pickup(), request.POST)
        if form.is_valid():
            form.save()
        else:
            for field, error in form.errors.items():
                messages.error(request, mark_safe(f'{field}: {error}'), extra_tags='danger')
    return return_to_previous_location(request)


@login_required
def set_job_pickup_location(request, job_id=None):
    if request.method == 'POST':
        if job_id is not None:
            job = get_object_or_404(MapJob.objects.of_member(request.user.member), id=job_id)
            form = PickupLocationForm(request.POST, instance=job, prefix=job_id)
        else:
            form = AllPickupLocationForm(request.POST, member=request.user.member)
        if form.is_valid():
            form.save()
            messages.success(request, _("Gewünschter Abholort wurde geändert."))
        else:
            for field, error in form.errors.items():
                messages.error(request, mark_safe(f'{field}: {error}'), extra_tags='danger')
    return return_to_previous_location(request)
