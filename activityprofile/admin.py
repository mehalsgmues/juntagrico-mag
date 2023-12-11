from ckeditor.widgets import CKEditorWidget
from django import forms
from django.contrib import admin
from juntagrico.admins.inlines.contact_inline import ContactInline
from juntagrico.dao.activityareadao import ActivityAreaDao
from juntagrico.entity.jobs import ActivityArea
from juntagrico.util.admin import queryset_for_coordinator, formfield_for_coordinator
from polymorphic.admin import PolymorphicInlineSupportMixin

from .models import ActivityProfile


class ActivityProfileAdminForm(forms.ModelForm):
    description = forms.CharField(label='Beschreibung', widget=CKEditorWidget())

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


class ActivityProfileAdmin(PolymorphicInlineSupportMixin, admin.ModelAdmin):
    form = ActivityProfileAdminForm
    search_fields = ('activity_area__name', 'activity_area__description', 'clothing', 'days', 'email', 'introduction',
                     'jobs_more', 'group_extras', 'learn', 'other_communication', 'wanted_for')
    list_display = ('__str__', 'group_emails', 'chat', 'minimum_size', 'target_size')
    list_filter = ('flexible', 'alone', 'in_groups', 'wanted')
    readonly_fields = ('activity_area',)

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            return super().get_readonly_fields(request, obj)
        return set()

    def get_queryset(self, request):
        return queryset_for_coordinator(self, request, 'activity_area__coordinator')

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        fields.remove('description')
        if obj:
            fields.remove('activity_area')
            fields.insert(0, 'activity_area')
            fields.insert(1, 'description')
        return fields

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # limit choices for area admins
        kwargs = formfield_for_coordinator(request,
                                           db_field.name,
                                           'activity_area',
                                           'juntagrico.is_area_admin',
                                           ActivityAreaDao.areas_by_coordinator)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(ActivityProfile, ActivityProfileAdmin)
