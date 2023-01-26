from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@staff_member_required
def share_progress_preview(request):
    return render(request, 'mag/share_progress_preview.html')


@login_required
def bep(request):
    return render(request, 'mag/bep.html')


@login_required
def price_change(request):
    return render(request, 'mag/price_change.html')
