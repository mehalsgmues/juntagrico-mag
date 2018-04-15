# -*- coding: utf-8 -*-

from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse

from juntagrico.models import Member

import json

# API    
@staff_member_required
def api_emaillist(request):
    """prints comma separated list of member emails"""
    # get emails
    return HttpResponse(', '.join( Member.objects.filter(inactive = False).values_list('email', flat=True) ))
