import threading

from django.core.management import call_command
from juntagrico.backends.email import BaseEmailBackend

from juntagrico_mailqueue.models import EmailMessage, EmailTo


class EmailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        email_messages = self.clean_messages(email_messages)
        if count := len(email_messages):
            for message in email_messages:
                message_obj = EmailMessage.objects.create(
                    subject=message.subject,
                    body=message.body,
                    from_email=message.from_email,
                    to=message.to,
                    cc=message.cc,
                    alternatives=getattr(message, 'alternatives', None),
                    attachments=message.attachments,
                    headers=message.extra_headers,
                    reply_to=message.reply_to,
                )
                for recipient in message.bcc:
                    EmailTo.objects.create(
                        email=recipient,
                        message=message_obj,
                    )

            # Start sending emails in daemon thread
            t = threading.Thread(target=call_command, args=['sendmails'], daemon=True)
            t.start()
        return count
