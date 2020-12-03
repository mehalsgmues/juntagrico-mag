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

    # jobs view override
    path('my/jobs', juntagrico_calendar.job_calendar, name='jobs'),

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
    path('my/export/subscriptions', mehalsgmues.excel_export_subscriptions, name='export-subscriptions'),

    # stats
    path('stats/', mehalsgmues.stats, name='mag-stats'),

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
    path('shares/preview/', mehalsgmues.share_progress_preview),

    # keep working
    path('my/order/share/', juntagrico_subscription.manage_shares, name='share-order'),
]
