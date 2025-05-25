from django.urls import reverse
from django.utils.translation import gettext as _

from mapjob.models import MapJob


def get_map_data(jobs, extra_colors=None, legend=True, urls=False):
    result = {}

    colors = {
        MapJob.Progress.OPEN: "#ff0000",
        MapJob.Progress.NEED_MORE: "#ff8800",
        MapJob.Progress.PICKED_UP: "#ffff00",
        MapJob.Progress.DELIVERED: "#00ff00",
    }
    colors.update(extra_colors or {})

    job_geo = []
    for map_job in jobs:
        geo = map_job.geo_area
        geo['properties'].update({
            'id': map_job.id,
            'status': map_job.progress,
        })
        if not legend:
            geo['properties']['color'] = colors[map_job.progress]
        if urls:
            geo['properties']['url'] = reverse('job', args=[map_job.id])
        job_geo.append(geo)

    result['data'] = job_geo

    if legend:
        result['legend'] = {
            p: [p.label, colors[p]] for p in MapJob.Progress if p in colors
        }
        result['legend']["default"] = [_("Andere"), "#000000"]

    return result
