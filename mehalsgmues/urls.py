"""mehalsgmues URL Configuration
"""
from django.urls import path, include
from django.contrib import admin
import juntagrico
from mehalsgmues import views as mehalsgmues

urlpatterns = [
    # pdf (override)
    path('my/pdf/depotlist', mehalsgmues.depot_list),
    path('my/pdf/depotoverview', mehalsgmues.depot_overview),
    path('my/pdf/amountoverview', mehalsgmues.amount_overview),

    path(r'admin/', admin.site.urls),
    path(r'', include('juntagrico.urls')),
    path(r'', juntagrico.views.home),
    path(r'', include('juntagrico_crowdfunding.urls')),
    path(r'impersonate/', include('impersonate.urls')),

    # report builder
    path(r'report_builder/', include('report_builder.urls')),

    # API
    path(r'wochenmail/', mehalsgmues.api_emaillist),

    # stats
    path('stats/', mehalsgmues.stats),

    # Discourse SSO
    path('sso/', mehalsgmues.sso),
]
