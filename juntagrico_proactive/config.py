# encoding: utf-8

from django.conf import settings


class ProactiveConfig:
    def __init__(self):
        pass

    @staticmethod
    def emails(key):
        if hasattr(settings, 'EMAILS'):
            if key in settings.EMAILS:
                return settings.EMAILS[key]
        return {
            'new_assignment_request_mail': 'proactive/mails/new_assignment_request_mail.txt',
            'edited_assignment_request_mail': 'proactive/mails/edited_assignment_request_mail.txt',
            'responded_assignment_request_mail': 'proactive/mails/responded_assignment_request_mail.txt',
            'confirmed_assignment_request_mail': 'proactive/mails/confirmed_assignment_request_mail.txt',
            'rejected_assignment_request_mail': 'proactive/mails/rejected_assignment_request_mail.txt',
            'notify_original_approver_mail': 'proactive/mails/notify_original_approver_mail.txt',
        }[key]
