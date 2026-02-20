from django.contrib import admin
from antispam.models import Access


class AccessAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'attempts', 'last_access')
    readonly_fields = ('last_access',)


admin.site.register(Access, AccessAdmin)
