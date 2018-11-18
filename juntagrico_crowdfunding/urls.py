"""juntagrico_bookkeeping URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
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
from django.conf.urls import url
from juntagrico_crowdfunding import views as crowdfunding

urlpatterns = [
    url(r'^cf/?$', crowdfunding.list_funding_projects),
    url(r'^cf/list/(?P<funding_project_id>.*?)/$', crowdfunding.list_fundables),
    url(r'^cf/view/(?P<fundable_id>.*?)/', crowdfunding.view_fundable),
    url(r'^cf/fund/(?P<fundable_id>.*?)/', crowdfunding.fund),
    url(r'^cf/confirm', crowdfunding.confirm),
    url(r'^cf/edit/order', crowdfunding.edit_order),
    url(r'^cf/edit/funder', crowdfunding.edit_funder),
    url(r'^cf/thanks', crowdfunding.thanks),
    url(r'^cf/contribution', crowdfunding.contribution),
]
