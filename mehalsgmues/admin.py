from django.contrib import admin
from juntagrico.util.admin import MyHTMLWidget

from django import forms

from juntagrico.entity.member import Member
from juntagrico.entity.share import Share
from juntagrico.admins.member_admin import MemberAdmin
from juntagrico.admins.forms.member_admin_form import MemberAdminForm

from django.urls import reverse
from juntagrico.config import Config
from django.utils.translation import gettext as _

from django.contrib.admin.models import LogEntry, DELETION
from django.utils.html import escape
from django.utils.safestring import mark_safe


class ExtendedMemberAdminForm(MemberAdminForm):
    def __init__(self, *a, **k):
        MemberAdminForm.__init__(self, *a, **k)
        member = k.get('instance')
        if member is not None:
            shares = Share.objects.filter(member=member)
            if len(shares) > 0:
                link = ", ".join([('<a href=%s>%s</a>' % (reverse('admin:juntagrico_share_change', args=(share.id,)),
                                                          share)) for share in shares])
            else:
                link = _('Kein/e/n {0}').format(Config.vocabulary('share'))
            self.fields['share_link'].initial = link

    share_link = forms.URLField(widget=MyHTMLWidget(), required=False, label='Anteilschein')


class ExtendedMemberAdmin(MemberAdmin):
    form = ExtendedMemberAdminForm


admin.site.unregister(Member)
admin.site.register(Member, ExtendedMemberAdmin)


class LogEntryAdmin(admin.ModelAdmin):

    date_hierarchy = 'action_time'

    readonly_fields = [f.name for f in LogEntry._meta.get_fields()]

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
        return request.user.is_superuser and request.method != 'POST'

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
            link = mark_safe(u'<a href="%s">%s</a>' % (
                reverse('admin:%s_%s_change' % (ct.app_label, ct.model), args=[obj.object_id]),
                escape(obj.object_repr),
            ))
        return link
    object_link.allow_tags = True
    object_link.admin_order_field = 'object_repr'
    object_link.short_description = u'object'


admin.site.register(LogEntry, LogEntryAdmin)