import datetime

from django.conf import settings
from django.db.models import F
from django.db.models.functions import Greatest
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.module_loading import import_string
from juntagrico.config import Config
from juntagrico.views_subscription import MemberSignupView

from antispam.forms import EmailForm, ConfirmForm, EmailFormWithCaptcha
from antispam.models import EmailToken, Access


def signup(request):
    signup_manager = import_string(Config.signup_manager())(request)
    if signup_manager.get('main_member'):
        return HttpResponseRedirect(reverse('signup', args=('continue', '0'), query=request.GET))

    # clean old accesses
    old_access = Access.objects.filter(last_access__lt=timezone.now() - datetime.timedelta(1))
    old_access.filter(attempts__lt=10).delete()
    old_access.update(attempts=Greatest(0, F('attempts') - 10))
    # get current access
    access = Access.from_meta(request.META)

    form_class = EmailForm
    if access.attempts > 0 or request.META.get('HTTP_USER_AGENT') in settings.SUSPICIOUS:
        form_class = EmailFormWithCaptcha

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            access.attempts += 1
            access.save()
            if access.attempts > 5:
                return HttpResponseForbidden()
            uid = form.save()
            return HttpResponseRedirect(reverse('confirm-email', args=(uid,)))
    else:
        form = form_class()
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


class ProtectedMemberSignupView(MemberSignupView):
    def __init__(self):
        super().__init__()
        self.email_token = None
        self.initial_email = None

    def dispatch(self, request, *args, **kwargs):
        signup_manager = import_string(Config.signup_manager())(request)
        if main_member := signup_manager.get('main_member'):
            self.initial_email = main_member['email']
            return super().dispatch(request, *args, **kwargs)

        uid = kwargs.pop('uid')
        token = kwargs.pop('token')
        now = timezone.now()
        EmailToken.objects.filter(created__lt=now - datetime.timedelta(hours=1)).delete()
        EmailToken.objects.filter(consumed__lt=now - datetime.timedelta(minutes=15)).delete()
        self.email_token = EmailToken.objects.filter(uid=uid, token=token).first()
        if not self.email_token:
            return HttpResponseRedirect(reverse('pre-signup'))
        else:
            self.email_token.consumed = now
            self.email_token.save()
        self.initial_email = self.email_token.email
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        if self.initial_email:
            return initial | {'email': self.initial_email}
        return initial

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['email'].disabled = True
        return form

    def form_valid(self, form):
        if self.email_token:
            self.email_token.delete()
        return super().form_valid(form)
