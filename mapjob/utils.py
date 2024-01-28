from django.utils.translation import gettext as _

from mapjob.models import MapJob


def get_map_data(jobs, extra_colors=None):
    job_geo = []
    for map_job in jobs:
        geo = map_job.geo_area
        geo['properties'].update({
            'id': map_job.id,
            'status': map_job.progress,
        })
        job_geo.append(geo)

    colors = {
        MapJob.Progress.OPEN: "#ff0000",
        MapJob.Progress.NEED_MORE: "#ff8800",
        MapJob.Progress.PICKED_UP: "#ffff00",
        MapJob.Progress.DELIVERED: "#00ff00",
    }
    colors.update(extra_colors)

    legend = {
        p: [p.label, colors[p]] for p in MapJob.Progress if p in colors
    }
    legend["default"] = [_("Andere"), "#000000"]

    return {
        'data': job_geo,
        'legend': legend
    }
