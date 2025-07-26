from django.shortcuts import render
from juntagrico.view_decorators import any_permission_required

from juntagrico_mailqueue.models import EmailMessage


@any_permission_required('juntagrico.can_send_mails',
                         'juntagrico.is_depot_admin',
                         'juntagrico.is_area_admin')
def mail_queue(request, numsent=None):
    if numsent is not None or not request.user.has_perm('juntagrico_mailqueue.view_emailmessage'):
        # just show a summary
        return render(request, 'juntagrico_mailqueue/summary.html', {
            'sent': numsent,
        })
    else:
        # show the queue
        return render(request, 'juntagrico_mailqueue/queue.html', {
            'emails': EmailMessage.objects.all(),
        })
