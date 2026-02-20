from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render
from django.utils.translation import gettext as _

from juntagrico.views import email

from juntagrico_mailqueue.models import EmailMessage


@permission_required('juntagrico_mailqueue.view_emailmessage')
def mail_queue(request):
    return render(request, 'juntagrico_mailqueue/queue.html', {
        'emails': EmailMessage.objects.all(),
    })

def sent(request):
    # Change success message
    messages.success(request, 'Email sent.')
    storage = messages.get_messages(request)
    for message in storage:
        if message.level == messages.SUCCESS:
            message.message = _('E-Mail(s) wurde(n) in den Postausgang gelegt.')
    storage.used = False
    return email.sent(request)
