from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AdminSplitDateTime
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import gettext as _

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
    actions = ['copy_map_job']
    list_filter = ('pickup_location', 'progress') + JobAdmin.list_filter
    list_display = JobAdmin.list_display + ['pickup_location', 'progress', 'used_flyers', 'participants']
    search_fields = JobAdmin.search_fields + ['pickup_location__location__name', 'progress',
                                              'assignment__member__first_name',
                                              'assignment__member__last_name']

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


MapJob.participants.fget.short_description = _('Teilnehmende')


@admin.register(PickupLocation)
class PickupLocationAdmin(admin.ModelAdmin):
    list_display = ['location', 'available_flyers']
    search_fields = ['location__name', 'available_flyers']
    autocomplete_fields = ['location']
