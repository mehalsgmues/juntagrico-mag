from django import template

from juntagrico_mailqueue.models import EmailMessage, EmailTo

register = template.Library()


@register.inclusion_tag('juntagrico_mailqueue/outbox_banner.html')
def outbox_banner(show_empty=False, can_see_outbox=True):
    return {
        'emails': EmailMessage.objects.all().count(),
        'show_empty': show_empty,
        'can_see_outbox': can_see_outbox,
        'recipients': EmailTo.objects.all().count(),
        'errors': EmailMessage.objects.filter(failed=True).values('last_error'),
    }
