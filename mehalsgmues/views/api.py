import vobject
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.utils import timezone
from juntagrico.entity.member import Member


@staff_member_required
def api_emaillist(request):
    """prints comma separated list of member emails"""
    sep = request.GET.get('sep', ', ')
    format = request.GET.get('format', 'plain')
    emails = sep.join(Member.objects.exclude(deactivation_date__lte=timezone.now().date()).values_list('email', flat=True))
    if format == 'plain':
        # just display for copy
        return HttpResponse(emails)
    else:
        # create file for download
        if format.find(';') == -1:
            content_type = f'text/{format}'
            file_type = format
        else:
            content_type, file_type = format.split(';')
        response = HttpResponse(content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="emails.{file_type}"'
        response.write(emails)
        return response


@staff_member_required
def api_vcf_contacts(request):
    members = Member.objects.exclude(deactivation_date__lte=timezone.now().date())
    cards = []
    for member in members:
        card = vobject.vCard()

        attr = card.add('n')
        attr.value = vobject.vcard.Name(family=member.last_name, given=member.first_name)

        attr = card.add('fn')
        attr.value = member.get_name()

        attr = card.add('email')
        attr.value = member.email

        if member.mobile_phone:
            attr = card.add('tel')
            attr.value = member.mobile_phone
            attr.type_param = 'cell'

        if member.phone:
            attr = card.add('tel')
            attr.value = member.phone
            attr.type_param = 'home'

        attr = card.add('org')
        attr.value = ["meh als gmües"]
        cards.append(card)

    response = HttpResponse(content_type='text/x-vcard')
    response['Content-Disposition'] = 'attachment; filename="members.vcf"'
    response.write("".join([card.serialize() for card in cards]))
    return response
