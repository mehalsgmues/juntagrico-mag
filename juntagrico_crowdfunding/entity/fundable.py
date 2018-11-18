from django.db import models

from math import ceil
from juntagrico_crowdfunding.models import FundingProject

class Fundable(models.Model):
    """
    A fundable object category
    """

    name = models.CharField('Name', max_length=100)
    description = models.TextField('Beschreibung')
    funding_project = models.ForeignKey(FundingProject, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField('Gesamtzahl')
    price = models.DecimalField('Preis/Einheit', max_digits=9 ,decimal_places=2)
    #allowFractions = models.BooleanField('Erlaube Teilbeiträge auf Einheiten')
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Unterstützungsart'
        verbose_name_plural = 'Unterstützungsarten'

    @property
    def available(self):
        return ceil( self.quantity - self.funded/self.price )

    @property
    def funded(self):
        funded = 0
        for funds in self.fund_set.all():
            funded += funds.contribution
        return funded

    @property
    def funded_ratio(self):
        return self.funded/(self.price*self.quantity)*100

    @property
    def is_funded(self):
        return self.funded >= self.price*self.quantity
