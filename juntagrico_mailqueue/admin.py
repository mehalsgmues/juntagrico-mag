from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from juntagrico_mailqueue.models import EmailMessage, EmailTo


class EmailToInline(admin.TabularInline):
    model = EmailTo
    extra = 0


class EmailMessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'created_on', 'from_email', 'reply_to', 'failed')
    readonly_fields = ('created_on',)
    inlines = [EmailToInline]
    actions = ['unfail']

    @admin.action(description=_('Fehler Zurücksetzen'))
    def unfail(self, request, queryset):
        queryset.update(failed=False)


admin.site.register(EmailMessage, EmailMessageAdmin)
