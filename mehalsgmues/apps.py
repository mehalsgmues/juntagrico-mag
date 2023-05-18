from datetime import date
from decimal import Decimal

from django.apps import AppConfig
from django.contrib import admin
from django.conf import settings
from django.db.models import Exists, OuterRef
from django.utils.html import escape
from django.utils.safestring import mark_safe


class MehAlsGmuesConfig(AppConfig):
    name = 'mehalsgmues'
    verbose_name = "meh als gmües"

    def ready(self):
        from . import signals

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

        # contact IT on signup
        def contact_admin_link(text):
            return mark_safe(
                escape(
                    text
                ).format('<a href="mailto:{0}">{0}</a>'.format(settings.IT_EMAIL))
            )

        from juntagrico.forms import MemberProfileForm
        MemberProfileForm.contact_admin_link = staticmethod(contact_admin_link)

        # patch price calculations
        def part_old_price(self):
            if self.price == 1200:
                return Decimal('1000.00')
            elif self.price == 1000:
                return Decimal('900.00')
            else:
                return self.price

        from juntagrico.entity.subtypes import SubscriptionType
        SubscriptionType.old_price = property(part_old_price)

        def sub_old_price(self):
            return sum(part.type.old_price for part in self.active_parts.all())

        from juntagrico.entity.subs import Subscription
        Subscription.old_price = property(sub_old_price)

        def sub_future_price(self):
            return sum(part.type.price for part in self.future_parts.all())

        Subscription.future_price = property(sub_future_price)

        # tune people admin
        from juntagrico.entity.share import Share

        @admin.display(
            boolean=True,
            ordering=Exists(Share.objects.filter(member=OuterRef('pk')).exclude(payback_date__lt=date.today())),
            description='Mitglied'
        )
        def is_member(self, obj):
            return obj.share_set.exclude(payback_date__lt=date.today()).exists()

        from juntagrico.admin import MemberAdminWithShares
        from mehalsgmues.admin import IsMemberFilter
        MemberAdminWithShares.is_member = is_member
        MemberAdminWithShares.list_display[-1] = 'is_member'
        MemberAdminWithShares.list_filter.insert(0, IsMemberFilter)
        del MemberAdminWithShares.fieldsets[-4]  # remove status
