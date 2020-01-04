from django.template.loader import get_template
from django.utils.translation import gettext as _

from juntagrico.config import Config
from juntagrico.mailer import send_mail, get_server

from juntagrico_proactive.config import ProactiveConfig
from juntagrico_proactive.dao.assignmentrequestdao import AssignmentRequestDao

'''
Server generated Emails
'''


def base_dict(add=None):
    add = add or {}
    add['serverurl'] = get_server()
    return add


def get_approver_emails(assignment_request):
    receivers = []
    if assignment_request.approver:
        # Notify approver if defined
        receivers.append(assignment_request.approver.email)
    else:
        # Otherwise inform all that should be notified on unapproved assignments
        for notified in AssignmentRequestDao.all_notified_on_unapproved_assignments():
            receivers.append(notified.email)
    if not receivers:
        # Nobody? Send it to the info mail then
        receivers.append(Config.info_email())
    return receivers


def send_request_mail(assignment_request):
    d = base_dict({'assignment_request': assignment_request})
    plaintext = get_template(ProactiveConfig.emails('new_assignment_request_mail'))

    content = plaintext.render(d)
    send_mail(Config.organisation_name()+' - Neue Böhnli-Anfrage', content, Config.info_email(),
              get_approver_emails(assignment_request))


def notify_original_approver_mail(assignment_request, new_approver):
    """
    notify original approver, if another approver handled the request
    """
    if assignment_request.approver and assignment_request.approver != new_approver:
        d = base_dict({
            'assignment_request': assignment_request,
            'new_approver': new_approver
        })
        plaintext = get_template(ProactiveConfig.emails('notify_original_approver_mail'))

        content = plaintext.render(d)
        send_mail(Config.organisation_name()+' - Böhnli-Anfrage erledigt', content, Config.info_email(),
                  [assignment_request.approver.email])


def resend_request_mail(assignment_request):
    d = base_dict({'assignment_request': assignment_request})
    plaintext = get_template(ProactiveConfig.emails('edited_assignment_request_mail'))

    content = plaintext.render(d)
    send_mail(Config.organisation_name()+' - Böhnli-Anfrage bearbeitet', content, Config.info_email(),
              get_approver_emails(assignment_request))


def respond_request_mail(assignment_request):
    d = base_dict({'assignment_request': assignment_request})

    if assignment_request.is_confirmed():
        subject = _('{} bestätigt').format(Config.vocabulary('assignment'))
        content = get_template(ProactiveConfig.emails('confirmed_assignment_request_mail')).render(d)
    elif assignment_request.is_rejected():
        subject = _('{} nicht bestätigt').format(Config.vocabulary('assignment'))
        content = get_template(ProactiveConfig.emails('rejected_assignment_request_mail')).render(d)
    else:
        subject = _('Rückfrage zu deinem/r {}').format(Config.vocabulary('assignment'))
        content = get_template(ProactiveConfig.emails('responded_assignment_request_mail')).render(d)

    send_mail(Config.organisation_name()+' - '+subject, content, Config.info_email(),
              [assignment_request.member.email], reply_to_email=assignment_request.approver.email)
