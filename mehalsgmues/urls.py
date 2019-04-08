"""mehalsgmues URL Configuration

The `urlpatterns` list routes URLs to views. 
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
import juntagrico
import juntagrico_crowdfunding
from mehalsgmues import views as mehalsgmues

urlpatterns = [
    # pdf (override)
    url('^my/pdf/depotlist', mehalsgmues.depot_list),
    url('^my/pdf/depotoverview', mehalsgmues.depot_overview),
    url('^my/pdf/amountoverview', mehalsgmues.amount_overview),

    url(r'^admin/', admin.site.urls), 
    url(r'^', include('juntagrico.urls')),
    url(r'^$', juntagrico.views.home),
    url(r'^', include('juntagrico_crowdfunding.urls')),
    url(r'^impersonate/', include('impersonate.urls')),

    # report builder
    url(r'^report_builder/', include('report_builder.urls')),

    # API
    url(r'^wochenmail/$', mehalsgmues.api_emaillist)
]
