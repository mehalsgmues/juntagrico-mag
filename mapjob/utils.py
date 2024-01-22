from django.db.models import Count, Q
from django.urls import reverse


def get_map_job_data(jobs, member):
    map_job_data = []
    for map_job in jobs.annotate(own=Count('assignment__member', filter=Q(assignment__member=member))):
        geo = map_job.geo_area
        geo['properties'].update({
            'url': reverse('job', args=(map_job.pk,)),
            'status': 101 if map_job.own else map_job.status_percentage()
        })
        map_job_data.append(geo)
    return {
        "legend": {
            101: ["Deine Gebiete", "#0000ff"],
            0: ["Offen", "#ff0000"],
            100: ["Vergeben/Erledigt", "#00ff00"],
            "default": ["Unterstützung Gesucht", "#ffff00"]
        },
        "data": map_job_data
    }
