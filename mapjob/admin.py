from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AdminSplitDateTime
from django.db.models import Count, Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from juntagrico.admins.filters import FutureDateTimeFilter

from juntagrico.admins.job_admin import JobAdmin
from juntagrico.dao.jobtypedao import JobTypeDao

from .models import MapJob, PickupLocation


class CopyMapJobForm(forms.Form):
    new_type = forms.ModelChoiceField(queryset=JobTypeDao.visible_types())
    new_datetime = forms.SplitDateTimeField(label=_('Neue Zeit'), widget=AdminSplitDateTime(), initial=timezone.now)

    def __init__(self, queryset, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset = queryset

    def save(self, commit=True):
        for job in self.queryset:
            MapJob.objects.create(
                type=self.cleaned_data['new_type'],
                time=self.cleaned_data['new_datetime'],
                slots=job.slots,
                infinite_slots=job.infinite_slots,
                multiplier=job.multiplier,
                geo_area=job.geo_area
            )


@admin.register(MapJob)
class MapJobAdmin(JobAdmin):
    fieldsets = [
        (None, { 'fields': JobAdmin.fields, },),
        (_('Flyer'),
            {'fields': ['geo_area', 'progress', 'pickup_location', 'used_flyers'],},
        ),
    ]
    fields = None
    actions = ['copy_map_job', 'set_complete', 'send_email']
    list_filter = ('pickup_location', 'progress',
                   ('type', admin.RelatedOnlyFieldListFilter), ('time', FutureDateTimeFilter))
    list_display = JobAdmin.list_display + ['pickup_location', 'progress', 'used_flyers', 'participants']
    search_fields = JobAdmin.search_fields + ['pickup_location__location__name', 'progress',
                                              'assignment__member__first_name',
                                              'assignment__member__last_name']

    def get_urls(self):
        # Needed to not break mass copy action on JobAdmin
        return super(JobAdmin, self).get_urls()

    @admin.action(description=_('Jobs kopieren...'))
    def copy_map_job(self, request, queryset):
        if 'apply' in request.POST:
            form = CopyMapJobForm(queryset, request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(request.get_full_path())
        else:
            form = CopyMapJobForm(queryset, initial={'new_type': queryset.first().type})

        return render(request,
                      'mapjob/admin/copy_map_job_intermediate.html',
                      context=dict(
                          self.admin_site.each_context(request),
                          media=self.media,
                          title=_('Jobs im Flächen kopieren'),
                          jobs=queryset,
                          form=form
                      ))

    @admin.action(description=_('Auf Abgeschlossen setzen'))
    def set_complete(self, request, queryset):
        queryset.update(progress=MapJob.Progress.COMPLETE)

    @admin.action(description=_('Eine E-Mail senden'))
    def send_email(self, request, queryset):
        emails = (queryset.exclude(assignment__member__email=None)
                  .order_by('assignment__member__email')
                  .values_list('assignment__member__email', flat=True)
                  .distinct())
        # Juntagrico requires POST for the "send email" form, which can not be used here.
        return render(request, 'mapjob/admin/email_list.html', context=dict(emails=emails))


MapJob.participants.fget.short_description = _('Teilnehmende')


class AreaInline(admin.TabularInline):
    model = MapJob
    readonly_fields = ('__str__', 'participants',)
    fields = ('__str__', 'participants', 'progress', 'used_flyers')
    ordering = ('-progress', 'used_flyers')
    show_change_link = True
    can_delete = False
    extra = 0
    max_num = 0

    @admin.display(description=_('Teilnehmende'))
    def participants(self, obj):
        return mark_safe(', '.join(
            ['<a href="' + reverse('admin:juntagrico_member_change', args=[p.id]) + '">' + str(p) + '</a>'
             for p in obj.participants]
        ))


@admin.register(PickupLocation)
class PickupLocationAdmin(admin.ModelAdmin):
    list_display = ['location', 'available_flyers', 'pending_areas']
    readonly_fields = ['pending_areas']
    search_fields = ['location__name', 'available_flyers']
    autocomplete_fields = ['location']
    inlines = [AreaInline]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _mapjob_count=Count('mapjob', filter=Q(
                mapjob__progress__in=[MapJob.Progress.OPEN, MapJob.Progress.NEED_MORE]
            )),
        )
        return queryset

    @admin.display(
        ordering='_mapjob_count',
        description=_('Verbleibende Gebiete'),
    )
    def pending_areas(self, obj):
        return obj.mapjob_set.need_pickup().count()
