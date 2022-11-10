from django.apps import AppConfig
from django.conf import settings
from django.utils.html import escape
from django.utils.safestring import mark_safe


class GodparentConfig(AppConfig):
    name = 'mehalsgmues'
    verbose_name = "meh als gmües"

    def ready(self):
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

        def contact_admin_link(text):
            return mark_safe(
                escape(
                    text
                ).format('<a href="mailto:{0}">{0}</a>'.format(settings.IT_EMAIL))
            )

        from juntagrico.forms import MemberProfileForm
        MemberProfileForm.contact_admin_link = staticmethod(contact_admin_link)
