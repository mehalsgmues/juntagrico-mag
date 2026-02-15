import random
import string
import uuid

from django.db import models


def random_string(length=4):
    return ''.join(random.choices(string.ascii_uppercase + string.digits * 5, k=length))


class EmailToken(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False)
    email = models.EmailField()
    token = models.CharField('Token', max_length=255, default=random_string)
    consumed = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    attempts = models.PositiveIntegerField(default=0)


class Access(models.Model):
    ip_address = models.GenericIPAddressField()
    attempts = models.PositiveIntegerField(default=0)
    last_access = models.DateTimeField(auto_now=True)
    meta = models.JSONField(default=dict)

    @classmethod
    def from_meta(cls, meta):
        x_forwarded_for = meta.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = meta.get('REMOTE_ADDR')
        return cls.objects.update_or_create(ip_address=ip, defaults={'meta': {
            key: meta.get(key) for key in ('HTTP_USER_AGENT', 'HTTP_ACCEPT_LANGUAGE', 'HTTP_ACCEPT', 'QUERY_STRING')
        }})[0]
