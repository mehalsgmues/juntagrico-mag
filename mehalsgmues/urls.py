"""mehalsgmues URL Configuration
"""
from django.urls import path, include
from django.contrib import admin
import juntagrico

from mehalsgmues.views import api, home_widgets, list_mgmt, other, sso, stats
from juntagrico_calendar import views as juntagrico_calendar
from juntagrico import views_subscription as juntagrico_subscription

urlpatterns = [
    # depot list management
    path('my/pdf/manage', list_mgmt.list_mgmt, name='lists-mgmt'),
    path('my/pdf/manage/success', list_mgmt.list_mgmt, {'success': True}, name='lists-mgmt-success'),
    path('my/pdf/manage/generate', list_mgmt.list_generate, name='lists-generate'),
    path('my/pdf/manage/generate/future', list_mgmt.list_generate, {'future': True}, name='lists-generate-future'),

    # /manage/share
    path('manage/share/canceledlist', other.share_unpaidlist, name='share-mgmt-unpaid'),

    # jobs view override
    path('my/jobs', juntagrico_calendar.job_calendar, name='jobs'),

    # member list override
    path('my/filters/active', other.filters_active, name='filters-active'),

    path(r'admin/shell/', include('django_admin_shell.urls')),
    path(r'admin/', admin.site.urls),
    path(r'', include('juntagrico.urls')),
    path(r'', juntagrico.views.home),
    path(r'', include('juntagrico_pg.urls')),
    # path(r'', include('juntagrico_crowdfunding.urls')),
    path(r'', include('juntagrico_calendar.urls')),
    path(r'', include('juntagrico_assignment_request.urls')),
    path(r'impersonate/', include('impersonate.urls')),

    # polling
    path(r'', include('juntagrico_polling.urls')),

    # API
    path(r'wochenmail/', api.api_emaillist, name='mag-mailing-list'),
    path(r'contacts/', api.api_vcf_contacts, name='mag-contact-list'),

    # exports
    path('my/export/mag/subscriptions', other.excel_export_subscriptions, name='export-subscriptions-mag'),

    # stats
    path('stats/indexes', stats.indexes, name='mag-indexes'),
    path('stats/subscriptions', stats.subscription_stats, name='mag-stats-subscription'),
    path('stats/assignments', stats.assignments, name='mag-stats-assignments'),
    path('stats', stats.stats, name='mag-stats'),
    path('stats/export', stats.stats_export, name='mag-stats-export'),
    path('stats/<slug:trunc>', stats.stats, name='mag-stats-by'),

    # Discourse SSO
    path('sso/', sso.sso),

    # OAuth
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('nextcloud/profile/', sso.nextcloud_profile),

    # short urls
    path('t/', include('shortener.urls', namespace='shortener')),

    # activity profile url
    path('activityprofile/', include('activityprofile.urls')),

    # share progress
    path('shares/preview/', home_widgets.share_progress_preview, name='shares-preview'),

    # keep working
    path('my/order/share/', juntagrico_subscription.manage_shares, name='share-order'),

    # BEP
    path('bep/', home_widgets.bep, name='bep'),

    # ajax
    path('ajax/notifications', other.ajax_notifications, name='ajax-notifications'),

    # depot changes
    path('manage/depot/changes', list_mgmt.depot_changes, name='manage-sub-depot-changes'),
    path('manage/depot/change/confirm/<int:subscription_id>', list_mgmt.depot_change_confirm,
         name='depot-change-confirm'),

    # godparents
    path('', include('juntagrico_godparent.urls')),

    # price change
    path('2023/', home_widgets.price_change, name='price_change'),

    # map job
    path('map/', include('mapjob.urls'))
]
