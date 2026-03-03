from django import forms
from django.contrib import admin
from djrichtextfield.widgets import RichTextWidget
from juntagrico.admins import AreaCoordinatorMixin
from polymorphic.admin import PolymorphicInlineSupportMixin

from .models import ActivityProfile


class ActivityProfileAdminForm(forms.ModelForm):
    description = forms.CharField(label='Beschreibung', widget=RichTextWidget(field_settings='activityprofile'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.adding = not self.instance.activity_area_id
        if self.adding:
            self.fields['description'].required = False
        else:
            self.fields['description'].initial = self.instance.activity_area.description

    def save(self, commit=True):
        if not self.adding:
            self.instance.activity_area.description = self.cleaned_data.get('description')
            self.instance.activity_area.save()
        return super().save(commit)

    class Meta:
        model = ActivityProfile
        fields = "__all__"


class ActivityProfileAdmin(PolymorphicInlineSupportMixin, AreaCoordinatorMixin, admin.ModelAdmin):
    form = ActivityProfileAdminForm
    search_fields = ('activity_area__name', 'activity_area__description', 'clothing', 'days', 'email', 'introduction',
                     'jobs_more', 'group_extras', 'learn', 'other_communication', 'wanted_for')
    list_display = ('__str__', 'group_emails', 'chat', 'minimum_size', 'target_size')
    list_filter = ('flexible', 'alone', 'in_groups', 'wanted')
    readonly_fields = ('activity_area',)
    path_to_area = 'activity_area'

    def get_area(self, obj):
        return obj.activity_area

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            return super().get_readonly_fields(request, obj)
        return set()

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        fields.remove('description')
        if obj:
            fields.remove('activity_area')
            fields.insert(0, 'activity_area')
            fields.insert(1, 'description')
        return fields


admin.site.register(ActivityProfile, ActivityProfileAdmin)
