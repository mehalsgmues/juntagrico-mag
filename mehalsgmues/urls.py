"""mehalsgmues URL Configuration
"""
from django.urls import path, include
from django.contrib import admin
import juntagrico
from mehalsgmues import views as mehalsgmues
from juntagrico_calendar import views as juntagrico_calendar
from juntagrico import views_subscription as juntagrico_subscription

urlpatterns = [
    # depot list management
    path('my/pdf/manage', mehalsgmues.list_mgmt, name='lists-mgmt'),
    path('my/pdf/manage/success', mehalsgmues.list_mgmt, {'success': True}, name='lists-mgmt-success'),
    path('my/pdf/manage/generate', mehalsgmues.list_generate, name='lists-generate'),
    path('my/pdf/manage/generate/future', mehalsgmues.list_generate, {'future': True}, name='lists-generate-future'),

    # /manage/share
    path('manage/share/canceledlist', mehalsgmues.share_unpaidlist, name='share-mgmt-unpaid'),

    # jobs view override
    path('my/jobs', juntagrico_calendar.job_calendar, name='jobs'),

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
    path(r'wochenmail/', mehalsgmues.api_emaillist, name='mag-mailing-list'),
    path(r'contacts/', mehalsgmues.api_vcf_contacts, name='mag-contact-list'),

    # exports
    path('my/export/mag/subscriptions', mehalsgmues.excel_export_subscriptions, name='export-subscriptions-mag'),

    # stats
    path('stats/indexes', mehalsgmues.indexes, name='mag-indexes'),
    path('stats', mehalsgmues.stats, name='mag-stats'),
    path('stats/export', mehalsgmues.stats_export, name='mag-stats-export'),
    path('stats/<slug:trunc>', mehalsgmues.stats, name='mag-stats-by'),

    # Discourse SSO
    path('sso/', mehalsgmues.sso),

    # OAuth
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('nextcloud/profile/', mehalsgmues.nextcloud_profile),

    # short urls
    path('t/', include('shortener.urls', namespace='shortener')),

    # activity profile url
    path('activityprofile/', include('activityprofile.urls')),

    # share progress
    path('shares/preview/', mehalsgmues.share_progress_preview, name='shares-preview'),

    # keep working
    path('my/order/share/', juntagrico_subscription.manage_shares, name='share-order'),

    # BEP
    path('bep/', mehalsgmues.bep, name='bep'),

    # ajax
    path('ajax/notifications', mehalsgmues.ajax_notifications, name='ajax-notifications'),

    # depot changes
    path('manage/depot/changes', mehalsgmues.depot_changes, name='depot-mgmt-changelist'),
    path('manage/depot/change/confirm/<int:subscription_id>', mehalsgmues.depot_change_confirm,
         name='depot-change-confirm'),

    # godparents
    path('', include('juntagrico_godparent.urls')),
]
