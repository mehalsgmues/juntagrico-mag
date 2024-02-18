from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, redirect
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from juntagrico.util import return_to_previous_location

from mapjob.forms import ReturnForm, PickupLocationForm, AllPickupLocationForm, PickupForm
from mapjob.models import MapJob


@login_required
def register(request, job_id):
    job = get_object_or_404(MapJob, id=job_id)
    member = request.user.member
    job.assign(request.user.member)
    # assume pickup in their own depot if this is a pickup location
    try:
        if member.subscription_current:
            location = member.subscription_current.depot.location.pickuplocation
            if location:
                job.pickup_location = location
                job.save()
    except ObjectDoesNotExist:
        pass
    return redirect('mapjob:member_dashboard')


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


@login_required
def pickup(request):
    if request.method == 'POST':
        form = PickupForm(MapJob.objects.of_member(request.user.member).need_pickup(), request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _('Danke fürs Abholen. Viel Erfolg beim Verteilen.'))
        else:
            for field, error in form.errors.items():
                messages.error(request, mark_safe(f'{field}: {error}'), extra_tags='danger')
    return return_to_previous_location(request)


@login_required
def set_job_progress(request, job_id, progress):
    job = get_object_or_404(MapJob.objects.of_member(request.user.member), id=job_id)
    job.progress = progress
    job.save()
    if progress == MapJob.Progress.NEED_MORE:
        messages.warning(request, _('Alles klar. Ganz unten findest du die Formular für die Flyer-Abholung.'))
    if progress == MapJob.Progress.DELIVERED:
        messages.success(request, _('Fantastisch. Vielen Dank für deinen Flyer-Einsatz!'))
    return return_to_previous_location(request)


@login_required
def return_remaining(request):
    if request.method == 'POST':
        form = ReturnForm(request.POST)
        if form.is_valid():
            form.save()
            MapJob.objects.of_member(request.user.member).update(progress=MapJob.Progress.COMPLETE)
            messages.success(request, _('Vielen Dank für deinen Einsatz und fürs Zurückbringen der übrigen Flyer!'))
        else:
            for field, error in form.errors.items():
                messages.error(request, mark_safe(f'{field}: {error}'), extra_tags='danger')
    return return_to_previous_location(request)


@login_required
def complete(request):
    MapJob.objects.of_member(request.user.member).update(progress=MapJob.Progress.COMPLETE)
    messages.success(request, _('Vielen Dank für deinen Einsatz!'))
    return return_to_previous_location(request)
