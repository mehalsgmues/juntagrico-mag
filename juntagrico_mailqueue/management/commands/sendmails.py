from smtplib import SMTPException
from ssl import SSLError

from django.core import mail
from django.core.management.base import BaseCommand

from juntagrico_mailqueue.models import EmailMessage
from juntagrico_mailqueue.utils import Lock


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-l', '--limit', type=int, help='Maximum number of emails to send')

    def handle(self, *args, **options):
        with Lock('juntagrico_mailqueue.lock'):
            # TODO: add option to use another backend
            with mail.get_connection(backend='django.core.mail.backends.smtp.EmailBackend') as connection:
                count = 0
                emails = EmailMessage.objects.order_by('failed')  # first process what didn't fail previously
                for email in emails.iterator(1):
                    message = email.get_message(connection)
                    # stop if this email would exceed the maximum number of emails
                    # but always allow first email, as low limits would otherwise block emails with many recipients
                    count_recipients = len(message.to + message.cc)
                    count += count_recipients
                    if options['limit'] and count > options['limit'] and not count == count_recipients:
                        break
                    success = False
                    try:
                        # send email without bcc
                        if message.send():
                            success = True
                            # clear to and cc to not send again
                            email.to = []
                            email.cc = []
                            email.save()
                        message.cc = []

                        # send individual emails for every bcc
                        for recipient in email.recipients.all():
                            message.to = [recipient.email]
                            count += 1
                            if options['limit'] and count > options['limit']:
                                break
                            success = False
                            if message.send():
                                success = True
                                # cleanup processed recipients
                                recipient.delete()

                        # clean up sent emails
                        if not email.recipients.exists():
                            email.delete()
                    except (SMTPException, SSLError) as e:
                        # Catch SMTP error and store error message
                        email.last_error = str(e)
                        email.save()
                    finally:
                        # Remember if sending failed
                        if not success:
                            email.failed = True
                            email.save()
