"""mehalsgmues URL Configuration
"""
from django.urls import path, include
from django.contrib import admin
import juntagrico
from mehalsgmues import views as mehalsgmues
from juntagrico_calendar import views as juntagrico_calendar

urlpatterns = [
    # pdf (override)
    path('my/pdf/depotlist', mehalsgmues.depot_list),
    path('my/pdf/depotoverview', mehalsgmues.depot_overview),
    path('my/pdf/amountoverview', mehalsgmues.amount_overview),

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

    # API
    path(r'wochenmail/', mehalsgmues.api_emaillist),

    # exports
    path('my/export/subscriptions', mehalsgmues.excel_export_subscriptions, name='export-subscriptions'),

    # stats
    path('stats/', mehalsgmues.stats),

    # Discourse SSO
    path('sso/', mehalsgmues.sso),

    # OAuth
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('nextcloud/profile/', mehalsgmues.nextcloud_profile),
]
