from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def price_change(request):
    return render(request, 'mag/price_change.html')
