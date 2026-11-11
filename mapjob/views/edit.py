import json

from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from juntagrico.entity.jobs import JobType

from mapjob.models import MapJob
from mapjob.utils import get_map_data


def _error(message, status=400):
    return JsonResponse({'success': False, 'error': message}, status=status)


# properties that get_map_data adds to the geo_area for display. They must not be stored.
COMPUTED_PROPERTIES = ('id', 'status', 'color', 'url')


def _parse_geo_area(data):
    """Returns the GeoJSON feature from the request data, or None if it is missing or invalid."""
    geo_area = data.get('geo_area')
    if not isinstance(geo_area, dict) or geo_area.get('type') != 'Feature' or not geo_area.get('geometry'):
        return None
    properties = geo_area.setdefault('properties', {})
    for key in COMPUTED_PROPERTIES:
        properties.pop(key, None)
    return geo_area


def _load_json(request):
    """Returns the parsed JSON body, or None if it is not a JSON object."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


@staff_member_required
def edit_map_by_type(request, type_id):
    job_type = get_object_or_404(JobType, id=type_id)
    jobs = MapJob.objects.filter(type=type_id).not_canceled()
    return render(request, 'mapjob/edit_map.html', {
        'job_type': job_type,
        'map_job_data': get_map_data(jobs, extra_colors={MapJob.Progress.COMPLETE: "#0f0"}),
    })


@staff_member_required
@require_POST
def save_geo_area(request, job_id):
    """API endpoint to save a modified geo_area for a MapJob."""
    job = get_object_or_404(MapJob, id=job_id)
    data = _load_json(request)
    if data is None:
        return _error('Invalid JSON')
    geo_area = _parse_geo_area(data)
    if geo_area is None:
        return _error('Invalid GeoJSON format')
    if data.get('name'):
        geo_area['properties']['name'] = data['name']
    job.geo_area = geo_area
    job.save()
    return JsonResponse({'success': True})


@staff_member_required
@require_POST
def create_map_job(request):
    """API endpoint to create a new MapJob from a drawn polygon."""
    data = _load_json(request)
    if data is None:
        return _error('Invalid JSON')
    type_id = data.get('type_id')
    if not type_id:
        return _error('type_id is required')
    geo_area = _parse_geo_area(data)
    if geo_area is None:
        return _error('Invalid GeoJSON format')
    job_type = get_object_or_404(JobType, id=type_id)
    name = data.get('name') or 'Neues Gebiet'
    geo_area['properties']['name'] = name
    job = MapJob.objects.create(
        type=job_type,
        geo_area=geo_area,
        slots=data.get('slots', 1),
        infinite_slots=False,
        # time is required, but the actual start time of a MapJob is always computed (see MapJob.start_time)
        time=timezone.now() + timezone.timedelta(hours=1),
    )
    return JsonResponse({'success': True, 'job_id': job.id, 'name': name})


@staff_member_required
def get_map_job_info(request, job_id):
    """API endpoint to get MapJob info including assignments."""
    job = get_object_or_404(MapJob, id=job_id)
    assignments = list(job.assignment_set.select_related('member'))
    return JsonResponse({
        'id': job.id,
        'name': str(job),
        'canceled': job.canceled,
        'assignment_count': len(assignments),
        'member_names': [assignment.member.get_name() for assignment in assignments],
    })


@staff_member_required
@require_POST
def delete_map_job(request, job_id):
    """API endpoint to delete a MapJob (only if no assignments exist)."""
    job = get_object_or_404(MapJob, id=job_id)
    assignment_count = job.assignment_set.count()
    if assignment_count > 0:
        return _error(f'Dieses Gebiet hat {assignment_count} Anmeldungen und kann nicht gelöscht werden.', status=409)
    job.delete()
    return JsonResponse({'success': True})


@staff_member_required
@require_POST
def cancel_map_job(request, job_id):
    """API endpoint to cancel (absagen) a MapJob, setting the canceled flag."""
    job = get_object_or_404(MapJob, id=job_id)
    job.canceled = True
    job.save()
    return JsonResponse({'success': True})
