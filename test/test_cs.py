from django.contrib import auth
from django.contrib.auth.models import Permission
from django.core import mail
from django.urls import reverse

from juntagrico.models import Member, Share, Subscription
from juntagrico.tests import JuntagricoTestCase

from antispam.models import EmailToken


class CreateSubscriptionTests(JuntagricoTestCase):

    def testSignupLogout(self):
        self.client.force_login(self.member.user)
        user = auth.get_user(self.client)
        assert user.is_authenticated
        email_token = EmailToken.objects.create()
        self.client.get(reverse('member-create', args=[email_token.uid, email_token.token]))
        self.assertEqual(str(auth.get_user(self.client)), 'AnonymousUser')

    def testRedirect(self):
        response = self.client.get(reverse('cs-subscription'))
        self.assertEqual(response.status_code, 302)
        response = self.client.post(reverse('cs-subscription'))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('cs-depot'))
        self.assertEqual(response.status_code, 302)
        response = self.client.post(reverse('cs-depot'))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('cs-start'))
        self.assertEqual(response.status_code, 302)
        response = self.client.post(reverse('cs-start'))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('cs-co-members'))
        self.assertEqual(response.status_code, 302)
        response = self.client.post(reverse('cs-co-members'))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('cs-shares'))
        self.assertEqual(response.status_code, 302)
        response = self.client.post(reverse('cs-shares'))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('cs-summary'))
        self.assertEqual(response.status_code, 302)
        response = self.client.post(reverse('cs-summary'))
        self.assertEqual(response.status_code, 302)

    def testWelcome(self):
        response = self.client.get(reverse('welcome'))
        self.assertEqual(response.status_code, 200)

    def testSignup(self):
        self.member.user.user_permissions.add(
            Permission.objects.get(codename='notified_on_subscription_creation'))
        self.member.user.user_permissions.add(
            Permission.objects.get(codename='notified_on_member_creation'))
        self.member.user.user_permissions.add(
            Permission.objects.get(codename='notified_on_share_creation'))
        self.member.user.save()
        member_email = 'test@user.com'
        response = self.client.post(reverse('pre-signup'), {'email': member_email,})
        email_token = EmailToken.objects.first()
        self.assertRedirects(response, reverse('confirm-email', args=[email_token.uid]))
        response = self.client.post(reverse('confirm-email', args=[email_token.uid]), {
            'token': email_token.token
        })
        self.assertRedirects(response, reverse('member-create', args=[email_token.uid, email_token.token]))
        new_member_data = {
            'last_name': 'Last Name',
            'first_name': 'First Name',
            'addr_street': 'Street',
            'addr_zipcode': '8000',
            'addr_location': 'Zurich',
            'phone': '044',
            'mobile_phone': '',
            'birthday': '',
            'agb': 'on'
        }
        response = self.client.post(reverse('member-create', args=[email_token.uid, email_token.token]), new_member_data)
        self.assertRedirects(response, reverse('cs-subscription'))
        response = self.client.post(
            reverse('cs-subscription'),
            {
                'amount[1]': 1,
                'amount[2]': 0,
                'amount[3]': 0,
            }
        )
        self.assertRedirects(response, reverse('cs-depot'))
        response = self.client.post(
            reverse('cs-depot'),
            {
                'depot': 1,
            }
        )
        self.assertRedirects(response, reverse('cs-start'))
        response = self.client.post(
            reverse('cs-start'),
            {
                'start_date': '01.01.2020',
                'initial-start_date': '2020-01-01'
            }
        )
        self.assertRedirects(response, reverse('cs-co-members'))
        response = self.client.post(
            reverse('cs-shares'),
            {
                'shares_mainmember': 1
            }
        )
        self.assertRedirects(response, reverse('cs-summary'))
        # confirm summary
        response = self.client.post(reverse('cs-summary'))
        self.assertRedirects(response, reverse('welcome-with-sub'))
        self.assertEqual(Member.objects.filter(email=member_email).count(), 1)
        self.assertEqual(Share.objects.filter(member__email=member_email).count(), 1)
        self.assertEqual(Subscription.objects.filter(primary_member__email=member_email).count(), 1)
        self.assertEqual(len(mail.outbox), 6)  # token mail, welcome mail, share mail & 3 admin notifications
