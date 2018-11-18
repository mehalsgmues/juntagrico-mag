from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives

from juntagrico.config import Config
from juntagrico.mailer import send_mail_multi, get_server

from juntagrico_crowdfunding.config import CrowdfundingConfig

'''
Server generated Emails
'''

def send_fund_confirmation_mail(fund, password=None):

    plaintext = get_template(CrowdfundingConfig.emails('fund_confirmation_mail'))

    d = {
        'fund': fund,
        'password': password,
        'serverurl': get_server()
    }

    content = plaintext.render(d)

    print(content)

    msg = EmailMultiAlternatives(Config.organisation_name() + ' - Beitragsbestätigung', content, Config.info_email(),
                                 [fund.funder.email])
    send_mail_multi(msg)
