from datetime import date

from django.contrib import admin
from django.db.models import Q

from django.urls import reverse, NoReverseMatch

from django.contrib.admin.models import LogEntry, DELETION
from django.utils.html import escape
from django.utils.safestring import mark_safe


class IsMemberFilter(admin.SimpleListFilter):
    title = 'Mitgliedschaft'
    parameter_name = 'is_member'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Ja'),
            ('no', 'Nein'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.exclude(share=None).filter(Q(share__payback_date__gte=date.today()) | Q(share__payback_date__isnull=True)).distinct()
        if self.value() == 'no':
            return queryset.filter(Q(share__payback_date__lt=date.today()) | Q(share=None)).distinct()


class LogEntryAdmin(admin.ModelAdmin):

    date_hierarchy = 'action_time'

    list_filter = [
        'user',
        'content_type',
        'action_flag'
    ]

    search_fields = [
        'object_repr',
        'change_message'
    ]

    list_display = [
        'action_time',
        'user',
        'content_type',
        'object_link',
        'action_flag_',
        'change_message',
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def action_flag_(self, obj):
        flags = {
            1: "Addition",
            2: "Changed",
            3: "Deleted",
        }
        return flags[obj.action_flag]

    def object_link(self, obj):
        if obj.action_flag == DELETION:
            link = escape(obj.object_repr)
        else:
            ct = obj.content_type
            try:
                link = mark_safe(u'<a href="%s">%s</a>' % (
                    reverse('admin:%s_%s_change' % (ct.app_label, ct.model), args=[obj.object_id]),
                    escape(obj.object_repr),
                ))
            except NoReverseMatch:
                link = escape(obj.object_repr)
        return link
    object_link.allow_tags = True
    object_link.admin_order_field = 'object_repr'
    object_link.short_description = u'object'


admin.site.register(LogEntry, LogEntryAdmin)
