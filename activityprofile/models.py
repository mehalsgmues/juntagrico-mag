from django.core.files.storage import default_storage
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from multiselectfield import MultiSelectField
from ckeditor.fields import RichTextField
from django.db import models
from juntagrico.entity.jobs import ActivityArea


SEASON = ((1, 'Januar'),
          (2, 'Februar'),
          (3, 'März'),
          (4, 'April'),
          (5, 'Mai'),
          (6, 'Juni'),
          (7, 'Juli'),
          (8, 'August'),
          (9, 'September'),
          (10, 'Oktober'),
          (11, 'November'),
          (12, 'Dezember'))


class ActivityProfile(models.Model):
    """
    Model that represents a profile of an activity area
    """
    activity_area = models.OneToOneField(ActivityArea, related_name='profile', on_delete=models.CASCADE, verbose_name='Tätigkeitsbereich')

    image = models.URLField('Bild-URL', null=True, blank=True,
                            help_text='Direktlink zu einem Bild')

    image_credits = models.CharField('Bild-Namensnennung', max_length=100, null=True, blank=True,
                                     help_text='Falls für die Verwendung des Bilds eine Namensnennung erforderlich ist')

    image_credits_url = models.URLField('Bild-Namensnennung-URL', null=True, blank=True,
                                        help_text='Link zur Lizenz des Bilds (wenn erforderlich)')

    learn = RichTextField('Lernen / Vorkenntnisse', max_length=1500, null=True, blank=True,
                          help_text='Was kann das Mitglied in dieser Gruppe lernen? Welche Kenntnisse werden vorausgesetzt?')
    introduction = RichTextField('Einführung', max_length=1000, null=True, blank=True,
                                 help_text='Ist eine Einführung nötig?')

    minimum_size = models.PositiveSmallIntegerField('Mindestgrösse', default=1)
    target_size = models.PositiveSmallIntegerField('Wunschgrösse', default=0, null=True, blank=True)

    wanted = models.CharField('Interessierte Gesucht?', default='no', max_length=10,
                              choices=[('no', 'Nein'), ('yes', 'Ja'), ('urgent', 'Dringend')])

    wanted_for = models.CharField('Interessierte Gesucht für', max_length=300, default='', null=True, blank=True,
                                  help_text='Wofür genau werden Interessierte gesucht? (optional)')

    group_extras = RichTextField('Gruppe / Mitglieder', max_length=1000, null=True, blank=True,
                                 help_text='Weitere Informationen zur Gruppe und deren Mitglieder')

    clothing = RichTextField('Kleidung', max_length=1000, null=True, blank=True)

    season = MultiSelectField('Saison', choices=SEASON, null=True)

    flexible = models.BooleanField('Einsätze Flexibel möglich?', default=False,
                                   help_text='Können eingeführte Mitglieder, jederzeit selbständig Einsätze leisten?')
    alone = models.BooleanField('Einsätze alleine möglich?', default=False)
    in_groups = models.BooleanField('Einsätze in Gruppen möglich?', default=False)
    days = models.CharField('Tage', max_length=100, null=True, blank=True,
                            help_text='Welche Tage der Woche gibt es Einsätze?')
    jobs_more = RichTextField('Mehr Einsatzdetails', max_length=1000, null=True, blank=True,
                              help_text='Was muss für den Einsatz sonst noch beachtet werden?')

    children = RichTextField('Kinderbegleitung Möglich?', max_length=500, null=True, blank=True,
                             help_text='Falls ja, unter welchen Bedingungen. Falls nein, warum nicht?')

    email = models.EmailField('Gruppen-E-Mail', null=True, blank=True,
                              help_text='E-Mail-Verteiler der Gruppe (falls vorhanden). '
                                        'Wenn leer wird Koordinations-E-Mail angezeigt.')
    chat = models.URLField('Gruppen-Chat-Link', null=True, blank=True,
                           help_text='Link zu Chat der Gruppe in Telegram oder Whatsapp etc.')

    other_communication = models.CharField('Andere Kommunikationsmethoden', max_length=200, null=True, blank=True,
                                           help_text='Andere Links oder Beschreibungen, wie Mitglieder interagieren können.')

    @property
    def name(self):
        return self.activity_area.name

    @property
    def group_email(self):
        return self.email if self.email else self.activity_area.get_email()

    @property
    def output_file(self):
        return f'_activityprofile_pdfs/{self.name}.pdf'

    def __str__(self):
        return f'{self.name} Steckbrief'


@receiver(post_save, sender=ActivityProfile)
@receiver(post_save, sender=ActivityArea)
@receiver(m2m_changed, sender=ActivityArea.members.through)
def clear_pdf(sender, instance, **kwargs):
    if isinstance(instance, ActivityArea):
        instance = instance.profile
    default_storage.delete(instance.output_file)
