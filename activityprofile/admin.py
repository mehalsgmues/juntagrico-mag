from ckeditor.widgets import CKEditorWidget
from django import forms
from django.contrib import admin
from juntagrico.dao.activityareadao import ActivityAreaDao
from juntagrico.util.admin import queryset_for_coordinator, formfield_for_coordinator

from .models import ActivityProfile


class ActivityProfileAdminForm(forms.ModelForm):
    description = forms.CharField(label='Beschreibung', widget=CKEditorWidget())
    show_phone_number = forms.BooleanField(label='Telefonnummer anzeigen', required=False)
    coordinator_email = forms.EmailField(label='Koordinations-E-Mail', required=False,
                                         help_text='Kontakt einer Ansprechperson. '
                                                   'Wenn leer wird private E-Mail-Adresse von KoordinatorIn angezeigt.')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.adding = not self.instance.activity_area_id
        if self.adding:
            self.fields['description'].required = False
        else:
            self.fields['description'].initial = self.instance.activity_area.description
            self.fields['show_phone_number'].initial = self.instance.activity_area.show_coordinator_phonenumber
            self.fields['coordinator_email'].initial = self.instance.activity_area.email

    def save(self, commit=True):
        if not self.adding:
            self.instance.activity_area.description = self.cleaned_data.get('description')
            self.instance.activity_area.show_coordinator_phonenumber = self.cleaned_data.get('show_phone_number')
            self.instance.activity_area.email = self.cleaned_data.get('coordinator_email') or None
            self.instance.activity_area.save()
        return super().save(commit)

    class Meta:
        model = ActivityProfile
        fields = "__all__"


class ActivityProfileAdmin(admin.ModelAdmin):
    form = ActivityProfileAdminForm
    search_fields = ('name',)

    def get_queryset(self, request):
        return queryset_for_coordinator(self, request, 'activity_area__coordinator')

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        fields.remove('description')
        fields.remove('show_phone_number')
        fields.remove('coordinator_email')
        if obj:
            fields.insert(1, 'description')
            fields.insert(2, 'show_phone_number')
            fields.insert(3, 'coordinator_email')
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
