from django.core import mail
from django.db import models

from juntagrico_mailqueue.utils import AttachmentEncoder, AttachmentDecoder


class EmailMessage(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    subject = models.TextField()
    body = models.TextField()
    from_email = models.TextField()
    to = models.JSONField(default=list, blank=True)
    cc = models.JSONField(default=list, blank=True)
    alternatives = models.JSONField(default=list, blank=True)
    attachments = models.JSONField(default=list, blank=True, encoder=AttachmentEncoder, decoder=AttachmentDecoder)
    headers = models.JSONField(default=dict, blank=True)
    reply_to = models.JSONField(default=list, blank=True)
    failed = models.BooleanField(default=False)
    last_error = models.TextField(blank=True)

    def get_message(self, connection=None):
        args = [self.subject, self.body, self.from_email, self.to]
        kwargs = dict(
            cc=self.cc,
            reply_to=self.reply_to,
            attachments=self.attachments,
            headers=self.headers,
            connection=connection,
        )
        if self.alternatives:
            return mail.EmailMultiAlternatives(*args, **kwargs, alternatives=self.alternatives)
        return mail.EmailMessage(*args, **kwargs)


class EmailTo(models.Model):
    message = models.ForeignKey(EmailMessage, on_delete=models.CASCADE, related_name='recipients')
    email = models.TextField()
