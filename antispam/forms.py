import datetime

from captcha.fields import CaptchaField
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django import forms
from django.template.loader import get_template
from django.urls import reverse
from django.utils import timezone
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _, gettext_lazy
from juntagrico.config import Config
from juntagrico.entity.member import Member
from juntagrico.mailer import EmailSender, organisation_subject, base_dict

from antispam.models import EmailToken


class EmailForm(forms.Form):
    email = forms.EmailField(label=gettext_lazy("E-Mail-Adresse"))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3'
        self.helper.field_class = 'col-md-9'
        self.helper.layout = Layout(
            'email',
            FormActions(
                Submit('submit', _('Weiter'), css_class='btn-success'),
            )
        )

    def clean_email(self):
        email = self.cleaned_data['email']
        if Member.objects.filter(email=email).exists():
            raise forms.ValidationError(mark_safe(
                escape(_('Diese E-Mail-Adresse existiert bereits im System.')) +
                ' <a href="' + reverse("home") + '">' + escape(_('Hier geht\'s zum Login.')) + '</a>'
            ))
        return email

    def save(self):
        email = self.cleaned_data['email']
        # reset retry limit
        now = timezone.now()
        EmailToken.objects.filter(email=email, created__lt=now - datetime.timedelta(minutes=10)).delete()
        # create and send token
        token, created = EmailToken.objects.update_or_create(email=email)
        if created:
            EmailSender.get_sender(
                organisation_subject(_('Dein Anmeldelink')),
                get_template('antispam/email_token.txt').render(base_dict(
                    dict(uid=token.uid, token=token.token)
                )),
                from_email='noreply@' + Config.contacts('general').split('@')[1],
                to=[email]
            ).send()
        return token.uid


class EmailFormWithCaptcha(EmailForm):
    captcha = CaptchaField(
        label=_('Sicherheitsprüfung'),
        help_text=_('Gib die Buchstaben ein, die du auf dem Bild siehst.')
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout.insert(1, 'captcha')


class ConfirmForm(forms.Form):
    token = forms.CharField(label='Code')

    def __init__(self, uid, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.uid = uid
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3'
        self.helper.field_class = 'col-md-9'
        self.helper.layout = Layout(
            'token',
            FormActions(
                Submit('submit', _('Weiter'), css_class='btn-success'),
            )
        )

    def clean_token(self):
        token = self.cleaned_data['token'].upper()
        if not EmailToken.objects.filter(uid=self.uid, token=token).exists():
            email_token = EmailToken.objects.get(uid=self.uid)
            email_token.attempts = email_token.attempts + 1
            email_token.save()
            raise forms.ValidationError(_('Falscher Code'))
        return token
