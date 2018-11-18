from django.db import models

class FundingProject(models.Model):
    """
    A crowdfunding project
    """

    title = models.CharField('Titel', max_length=200)
    description = models.TextField('Beschreibung', blank=True, null=True)
    image = models.URLField('Bild-URL', blank=True, null=True)
    active = models.BooleanField('Aktiv')
    
    vocabulary_fundable = models.CharField('Bezeichnung: Unterstützungsart', max_length=200, default='Patenschaft')
    vocabulary_fundables = models.CharField('Bezeichnung: Unterstützungsarten', max_length=200, default='Patenschaften')
    
    vocabulary_whoIsSponsor = models.TextField('Formular: Patenschaftsnennung', default='Auf wen soll die Patenschaft lauten (Vorname(n))?')
    vocabulary_confirmOrder = models.TextField('Formular: Kauf bestätigen', default='Bei Bestätigung kaufe ich eine Patenschaft und mache damit eine Schenkung an die Genossenschaft MehalsGmües. Ich kriege eine Patenschaftsbestätigung (Karte - als Geschenk geeignet) per Post. Der Name, auf welchen die Patenschaft lautet, wird auf einer Tafel in der Gärtnerei verewigt.')
    vocabulary_confirmOrderButton = models.CharField('Formular: Button Verbindlich bestätigen', max_length=200, default='Verbindlich bestätigen')
    
    vocabulary_thankYouTitle = models.CharField('Titel: Dankeschön', max_length=200, default='Vielen Dank')
    vocabulary_thankYouMessage = models.TextField('Text: Dankeschön', default='ladida')
    
    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Unterstützungs-Projekt'
        verbose_name_plural = 'Unterstützungs-Projekte'
