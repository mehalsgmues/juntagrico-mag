from django.db import models

from django.contrib.auth.models import User

class Funder(models.Model):
    """
    A funder
    """

    user = models.OneToOneField(User, related_name='funder', on_delete=models.CASCADE)

    first_name = models.CharField('Vorname', max_length=30)
    last_name = models.CharField('Nachname', max_length=30)
    email = models.EmailField(unique=True)

    addr_street = models.CharField('Strasse', max_length=100)
    addr_zipcode = models.CharField('PLZ', max_length=10)
    addr_location = models.CharField('Ort', max_length=50)
    phone = models.CharField('Telefonnr', max_length=50, null=True, blank=True)
    
    def __str__(self):
        return "%s %s" % (self.first_name, self.last_name)

    class Meta:
        verbose_name = 'UnterstützerIn'
        verbose_name_plural = 'UnterstützerInnen'
