from django.db import models

from juntagrico_crowdfunding.models import Funder
from juntagrico_crowdfunding.models import Fundable

class Fund(models.Model):
    """
    A fund for a fundable
    """

    funder = models.ForeignKey(Funder, on_delete=models.CASCADE)
    sponsor = models.CharField('Pate(n)', max_length=100, blank=True)
    fundable = models.ForeignKey(Fundable, on_delete=models.CASCADE)
    contribution = models.DecimalField('Beitrag', max_digits=9 ,decimal_places=2)
    date_ordered = models.DateField('Bestellt am', auto_now_add=True, editable=True)
    date_paid = models.DateField('Bezahlt am', blank=True, null=True)
    message = models.TextField('Mitteilung', blank=True, null=True)
    comment = models.TextField('Kommentar', blank=True, null=True)
    
    def __str__(self):
        return 'Beitrag %s' % self.id

    class Meta:
        verbose_name = 'Unterstützung'
        verbose_name_plural = 'Unterstützungen'
