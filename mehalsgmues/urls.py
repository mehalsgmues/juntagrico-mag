"""mehalsgmues URL Configuration
"""
from django.urls import path, include
from django.contrib import admin

from mehalsgmues.views import api, home_widgets, other, sso, stats
from juntagrico_calendar import views as juntagrico_calendar
from juntagrico import views_subscription as juntagrico_subscription

urlpatterns = [
    # jobs view override
    path('my/jobs', juntagrico_calendar.job_calendar, name='jobs'),

    # member list override
    path('manage/member/active', other.MemberActiveView.as_view(), name='manage-member-active'),

    path('admin/shell/', include('django_admin_shell.urls')),
    path('admin/', admin.site.urls),
    path('', include('juntagrico.urls')),
    path('', include('juntagrico_mailqueue.urls')),
    path('', include('juntagrico_pg.urls')),
    # path('', include('juntagrico_crowdfunding.urls')),
    path('', include('juntagrico_calendar.urls')),
    path('', include('juntagrico_assignment_request.urls')),
    path('impersonate/', include('impersonate.urls')),

    # polling
    # path('', include('juntagrico_polling.urls')),

    # API
    path('wochenmail/', api.api_emaillist, name='mag-mailing-list'),
    path('contacts/', api.api_vcf_contacts, name='mag-contact-list'),

    # exports
    path('my/export/mag/subscriptions', other.excel_export_subscriptions, name='export-subscriptions-mag'),

    # stats
    path('stats/indexes', stats.indexes, name='mag-indexes'),
    path('stats/subscriptions', stats.subscription_stats, name='mag-stats-subscription'),
    path('stats/shares', stats.shares, name='mag-stats-share'),
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

    # keep working
    path('my/order/share/', juntagrico_subscription.manage_shares, name='share-order'),

    # ajax
    path('ajax/notifications', other.ajax_notifications, name='ajax-notifications'),

    # godparents
    path('jgo/', include('juntagrico_godparent.urls')),

    # price change
    path('2024/', home_widgets.price_change, name='price_change'),

    # map job
    path('map/', include('mapjob.urls'))
]
