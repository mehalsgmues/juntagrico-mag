from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from django.contrib.auth.models import User
from juntagrico_crowdfunding.entity.fundable import *
from juntagrico_crowdfunding.entity.fund import *


class FundInline(admin.TabularInline):
    model = Fund
    verbose_name = 'Unterstützung'
    verbose_name_plural = 'Unterstützungen'
    extra = 0


class FundableAdmin(admin.ModelAdmin):
    inlines = [FundInline]


class FundAdmin(admin.ModelAdmin):
    readonly_fields = ["date_ordered"]


admin.site.register(FundingProject)
admin.site.register(Fundable, FundableAdmin)
admin.site.register(Fund, FundAdmin)
admin.site.register(Funder)


# add funder inline
class FunderInline(admin.StackedInline):
    model = Funder
    max_num = 1
    can_delete = False


class CustomUserAdmin(UserAdmin):
    inlines = [FunderInline]


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
