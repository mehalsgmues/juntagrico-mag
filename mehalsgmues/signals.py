from django.dispatch import receiver
from django.template.loader import get_template
import html
from juntagrico.entity.member import Member
from juntagrico.mailer import EmailSender, organisation_subject, base_dict
from juntagrico.signals import depot_changed, area_joined, area_left


@receiver(depot_changed)
def on_depot_change(sender, **kwargs):
    EmailSender.get_sender(
        organisation_subject('Ein Mitglied hat das Depot geändert'),
        get_template('juntagrico/mails/admin/depot_changed.txt').render(base_dict(kwargs)),
        bcc=[Member.objects.get(pk=689).email]
    ).send()


@receiver(area_joined)
def on_area_join(sender, *, area, member, **kwargs):
    EmailSender.get_sender(
        organisation_subject(f'Willkommen in der Arbeitsgruppe {area.name}'),
        html.unescape(get_template('mag/mails/member/area_joined.txt').render(base_dict(dict(area=area, member=member, **kwargs)))),
        to=[member.email],
        reply_to=area.get_emails()
    ).send()


@receiver(area_left)
def on_area_leave(sender, *, area, member, **kwargs):
    EmailSender.get_sender(
        organisation_subject(f'Du hast die Arbeitsgruppe {area.name} verlassen'),
        f'Du bist nicht mehr in der Arbeitsgruppe {area.name}. Wir hoffen du hattest eine gute Zeit.',
        to=[member.email],
        reply_to=area.get_emails()
    ).send()
