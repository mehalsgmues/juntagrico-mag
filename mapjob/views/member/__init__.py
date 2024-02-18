from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from mapjob.forms import PickupForm, AllPickupLocationForm, ReturnForm
from mapjob.models import MapJob

from . import actions  # noqa: F401
from ...utils import get_map_data


@login_required
def available_areas(request):
    # available map jobs
    available_jobs = MapJob.objects.active().undelivered().with_free_slots()

    available_job_geo = []
    for map_job in available_jobs:
        geo = map_job.geo_area
        geo['properties'].update({
            'color': "#ff0000",
            'id': map_job.id,
        })
        available_job_geo.append(geo)

    return render(request, 'mapjob/dashboard/available_areas.html', {
        'past_jobs': MapJob.objects.completed().recent(60).of_member(request.user.member).exists(),
        'available_jobs': available_jobs,
        'map_job_data': {
            'available': {
                'data': available_job_geo
            }
        },
    })


@login_required
def delivery_dashboard(request):
    member = request.user.member
    # jobs of member
    own_jobs = MapJob.objects.active().of_member(member)
    if not own_jobs:
        return redirect('mapjob:available_areas')

    # pickup form
    pickup_form = None
    pickup_location_form = None
    pickup_jobs = own_jobs.need_pickup()
    if pickup_jobs:
        pickup_form = PickupForm(pickup_jobs)
        pickup_location_form = AllPickupLocationForm(initial={'pickup_location': pickup_jobs.first().pickup_location})

    # return form
    return_form = None
    if own_jobs.exists() and not own_jobs.undelivered().exists():
        return_form = ReturnForm(initial={'return_location': own_jobs.first().pickup_location})

    return render(request, 'mapjob/dashboard/delivering.html', {
        'own_jobs': own_jobs,
        'map_job_data': {
            'reserved': get_map_data(own_jobs)
        },
        'pickup_form': pickup_form,
        'pickup_location_form': pickup_location_form,
        'return_form': return_form,
    })
