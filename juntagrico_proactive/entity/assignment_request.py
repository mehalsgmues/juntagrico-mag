from datetime import datetime, date

from django.db import models
from django.utils.translation import gettext as _
from django.core.validators import MinValueValidator

from juntagrico.models import Assignment, Member, ActivityArea, JobType, RecuringJob
from juntagrico.config import Config

from juntagrico_proactive.mailer import respond_request_mail


class AssignmentRequest(models.Model):
    """
    A request to get an assignment
    """

    REQUESTED = 'RE'
    REJECTED = 'NO'
    CONFIRMED = 'CO'
    REQUEST_STATUS = [
        (REQUESTED, _('Beantragt')),
        (REJECTED, _('Abgelehnt')),
        (CONFIRMED, _('Bestätigt')),
    ]

    member = models.ForeignKey(Member, verbose_name=Config.vocabulary('member'), on_delete=models.CASCADE)
    assignment = models.OneToOneField(Assignment, verbose_name=Config.vocabulary('assignment'),
                                      blank=True, null=True, on_delete=models.PROTECT)
    amount = models.PositiveIntegerField(_('Wert'), default=1, validators=[MinValueValidator(1)])
    job_time = models.DateTimeField(_('Geleistet am'), default=datetime.now)
    request_date = models.DateField(_('Beantragt am'), default=date.today, blank=True, null=True)
    response_date = models.DateField(_('Beantwortet am'), blank=True, null=True)
    approver = models.ForeignKey(Member, verbose_name=_('Abgesprochen mit'), related_name=_('Referenz'),
                                 blank=True, null=True, on_delete=models.SET_NULL)

    description = models.TextField(_('Beschreibung'), max_length=1000, default='')
    activityarea = models.ForeignKey(ActivityArea, verbose_name=_('Tätigkeitsbereich'),
                                     blank=True, null=True, on_delete=models.SET_NULL)
    duration = models.PositiveIntegerField(_('Dauer in Stunden'), default=4)
    location = models.CharField(_('Ort'), max_length=100, blank=True, default='')

    status = models.CharField(max_length=2, choices=REQUEST_STATUS, default=REQUESTED)
    response = models.TextField(_('Antwort'), blank=True, null=True)
    
    def __str__(self):
        return _('%s Anfrage #%s') % (Config.vocabulary('assignment'), self.id)

    def is_confirmed(self):
        return self.status == self.CONFIRMED

    def is_rejected(self):
        return self.status == self.REJECTED

    @classmethod
    def pre_save(cls, sender, instance, **kwds):
        """
        Callback before saving assignment request
        """
        if instance.assignment is not None:
            cls._remove_assignment(instance)
        if instance.status == cls.CONFIRMED:
            # create fresh in any case
            cls._attach_assignment(instance)

    @classmethod
    def _attach_assignment(cls, instance):
        # create/use default activity_area if none specified
        if not instance.activityarea:
            instance.activityarea, created = ActivityArea.objects.get_or_create(
                name=_('Selbständige Einsätze'),
                defaults={
                    'coordinator': instance.approver,
                    'hidden': True
                }
            )
        # create job type if not exists
        job_name = f'_proactive_{instance.activityarea.id}_{instance.duration}_{instance.location}'
        job_type = JobType.objects.filter(name=job_name + '_public')
        if job_type:
            job_type = job_type[0]
        else:
            job_type, created = JobType.objects.get_or_create(
                name=job_name,
                defaults={
                    'displayed_name': _('Selbständiger Einsatz'),
                    'description': _('Dies ist ein automatisch erzeugter Einsatz.'),
                    'activityarea': instance.activityarea,
                    'duration': instance.duration,
                    'location': instance.location
                }
            )
        # create job with job type if not exists
        job, created = RecuringJob.objects.get_or_create(type=job_type, time=instance.job_time,
                                                         defaults={'slots': 1})
        if job.free_slots() == 0:
            job.slots += 1
            job.save()
        # add assignment to job
        assignment = Assignment.objects.create(member=instance.member, job=job, amount=instance.amount)
        # link request to assignment
        instance.assignment = assignment

    @classmethod
    def _remove_assignment(cls, instance):
        # Delete assignment and job, if it has no other assignments
        # the job type is not deleted
        delete_job = None
        if instance.assignment.job.occupied_places() == 1:
            delete_job = instance.assignment.job
        assignment_delete = instance.assignment
        instance.assignment = None
        instance.save()
        assignment_delete.delete()
        if delete_job:
            delete_job.delete()

    class Meta:
        verbose_name = _('%s Anfrage') % Config.vocabulary('assignment')
        verbose_name_plural = _('%s Anfragen') % Config.vocabulary('assignment')
        permissions = (
            ('can_confirm_assignments', _('Kann selbständige Arbeitseinsätze bestätigen')),
            ('notified_on_unapproved_assignments', _('Wird über nicht abgesprochene Arbeitseinsätze informiert')),
        )
