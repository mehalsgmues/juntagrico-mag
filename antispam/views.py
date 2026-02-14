import datetime

from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from juntagrico.util.sessions import SessionObjectManager, CSSessionObject
from juntagrico.views_subscription import SignupView

from antispam.forms import EmailForm, ConfirmForm
from antispam.models import EmailToken


def signup(request):
    som = SessionObjectManager(request, 'create_subscription', CSSessionObject)
    session_object = som.data
    if session_object.edit:
        return HttpResponseRedirect(reverse('signup', args=('continue', '0')))

    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            uid = form.save()
            return HttpResponseRedirect(reverse('confirm-email', args=(uid,)))
    else:
        form = EmailForm()
    return render(request, 'antispam/signup.html', {
        'form': form,
    })


def confirm(request, uid):
    email_token = get_object_or_404(EmailToken, uid=uid, consumed=None)
    if email_token.attempts >= 3:
        email_token.delete()
        return HttpResponseRedirect(reverse('pre-signup'))
    if request.method == 'POST':
        form = ConfirmForm(uid, request.POST)
        if form.is_valid():
            return HttpResponseRedirect(reverse('member-create', args=(uid, form.cleaned_data['token'])))
    else:
        form = ConfirmForm(uid)
    return render(request, 'antispam/confirm.html', {
        'form': form,
        'email': email_token.email,
    })


class ProtectedMemberSignupView(SignupView):
    def __init__(self):
        super().__init__()
        self.uid = None
        self.token = None

    def dispatch(self, request, *args, **kwargs):
        som = SessionObjectManager(request, 'create_subscription', CSSessionObject)
        session_object = som.data
        if session_object.edit:
            return super().dispatch(request, *args, **kwargs)

        self.uid = kwargs.pop('uid')
        self.token = kwargs.pop('token')
        now = timezone.now()
        EmailToken.objects.filter(created__lt=now - datetime.timedelta(hours=1)).delete()
        EmailToken.objects.filter(consumed__lt=now - datetime.timedelta(minutes=15)).delete()
        email_token = EmailToken.objects.filter(uid=self.uid, token=self.token)
        if not email_token.exists():
            return HttpResponseRedirect(reverse('pre-signup'))
        else:
            email_token.update(consumed=now)
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not self.cs_session.edit:
            email = request.POST.get('email')
            if not EmailToken.objects.filter(uid=self.uid, token=self.token, email=email).exists():
                form = self.get_form()
                form.add_error('email', 'Verwende die gleiche E-Mail-Adresse wie zuvor.')
                return self.form_invalid(form)
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        EmailToken.objects.filter(uid=self.uid).delete()
        return super().form_valid(form)
