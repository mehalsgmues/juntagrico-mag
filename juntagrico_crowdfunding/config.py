# encoding: utf-8

from django.conf import settings

class CrowdfundingConfig:
    def __init__(self):
        pass

    @staticmethod
    def emails(key):
        if hasattr(settings, 'EMAILS'):
            if key in settings.EMAILS:
                return settings.EMAILS[key]
        return {'fund_confirmation_mail': 'cf/mails/fund_confirmation_mail.txt',
                }[key]
