from datetime import date

from django.apps import AppConfig
from django.contrib import admin
from django.db.models import Exists, OuterRef


class MehAlsGmuesConfig(AppConfig):
    name = 'mehalsgmues'
    verbose_name = "meh als gmües"
    default_auto_field = 'django.db.models.AutoField'

    def ready(self):
        # connect signals
        from . import signals  # noqa: F401

        # add export resources
        from juntagrico.admins.subscription_admin import SubscriptionAdmin
        from mehalsgmues.resources.subscription import SubscriptionByTypeResource
        SubscriptionAdmin.resource_classes.append(SubscriptionByTypeResource)

        # godparent tuning
        from juntagrico_godparent.forms import GodparentForm
        GodparentForm.append_help_texts = dict(
            max_godchildren='<br>Bei Möglichkeit versucht die Patenschaftskoordination dir Neumitglieder zuzuteilen, '
                            'die zum selben Zeitfenster verfügbar sind.'
        )
        GodparentForm.override_help_texts = dict(
            languages='In dieser Sprache/diesen Sprachen könnte ich mich mit dem Neumitglied verständigen.',
            areas='Aktuell bist du in diesen Arbeitsgruppen eingetragen. '
                  'Bitte prüfe ob dies noch stimmt.<br>'
                  'Wenn du die Auswahl hier änderst, wirst du in die entsprechenden Arbeitsgruppen eingetragen.'
        )
        GodparentForm.override_labels = dict(
            areas='Arbeitsgruppen'
        )

        # patch price calculations
        def sub_future_price(self):
            return sum(part.type.price for part in self.future_parts.all())

        from juntagrico.entity.subs import Subscription
        Subscription.future_price = property(sub_future_price)

        # tune people admin
        from juntagrico.entity.share import Share

        @admin.display(
            boolean=True,
            ordering=Exists(Share.objects.filter(member=OuterRef('pk')).exclude(termination_date__lt=date.today())),
            description='Mitglied'
        )
        def is_member(self, obj):
            return obj.share_set.exclude(termination_date__lt=date.today()).exists()

        from juntagrico.admin import MemberAdminWithShares
        from mehalsgmues.admin import IsMemberFilter
        MemberAdminWithShares.is_member = is_member
        MemberAdminWithShares.list_display[-1] = 'is_member'
        MemberAdminWithShares.list_filter.insert(0, IsMemberFilter)
        del MemberAdminWithShares.fieldsets[-3]  # remove status
