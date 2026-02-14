import random
import string
import uuid

from django.db import models


def random_string(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


class EmailToken(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False)
    email = models.EmailField()
    token = models.CharField('Token', max_length=255, default=random_string)
    consumed = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    attempts = models.PositiveIntegerField(default=0)
