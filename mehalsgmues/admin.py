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