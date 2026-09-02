from io import BytesIO

from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import render
from django.template.loader import get_template

from django.contrib.admin.views.decorators import staff_member_required
from juntagrico.mailer import base_dict
from juntagrico.util.pdf import internal_storage
from xhtml2pdf import pisa

from activityprofile.models import ActivityProfile


def render_to_pdf_storage(template_name, renderdict, filename):
    """ copied and fixed here in the meantime
    """
    if internal_storage.exists(filename):
        internal_storage.delete(filename)
    rendered_html = get_template(template_name).render(renderdict)
    pdf = BytesIO()
    pisa.CreatePDF(BytesIO(str(rendered_html).encode('utf-8')), dest=pdf, path='.')
    internal_storage.save(filename, ContentFile(pdf.getvalue()))


def return_pdf_http(filename):
    """ override to fix filename
    """
    if internal_storage.exists(filename):
        with internal_storage.open(filename) as pdf_file:
            content = pdf_file.read()
        content_disposition = f'attachment; filename="{filename.split("/")[-1]}"'
        response = HttpResponse(content, content_type='application/pdf')
        response['Content-Disposition'] = content_disposition
        return response
    else:
        return HttpResponseServerError()


@staff_member_required
def print_pdf(request, area_id):
    render_dict = base_dict({
        'activity': ActivityProfile.objects.get(activity_area_id=area_id)
    })
    filename = render_dict['activity'].output_file
    if not internal_storage.exists(filename):
        render_to_pdf_storage('activityprofile/print.html', render_dict, filename)
    return return_pdf_http(filename)


@login_required(login_url='activityprofile:external-login')
def iframe(request, area_id):
    activity_profile = ActivityProfile.objects.get(activity_area_id=area_id)
    render_dict = {
        'area': getattr(activity_profile, 'activity_area', None),
        'area_checked': request.user.member in activity_profile.activity_area.members.all()
    }
    return render(request, 'activityprofile/iframe.html', render_dict)
