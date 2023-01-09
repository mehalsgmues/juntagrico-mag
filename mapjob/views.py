from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import render
from django.urls import reverse

from mapjob.models import MapJob


@login_required
def job_map(request):
    map_job_data = []
    for map_job in MapJob.objects.all().annotate(own=Count('assignment__member', filter=Q(assignment__member=request.user.member))):
        geo = map_job.geo_area
        geo['properties'].update({
            'url': reverse('job', args=(map_job.pk,)),
            'status': 101 if map_job.own else map_job.status_percentage()
        })
        map_job_data.append(geo)
    return render(request, 'mapjob/job_map.html', {
        'map_job_data': map_job_data
    })
