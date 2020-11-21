from django.urls import reverse

from test import MagTestCase


class MagTests(MagTestCase):

    def setUp(self):
        super().setUp()
        self.admin = self.admin()

    def test_depolist(self):
        # without access
        self.assertGet(reverse('lists-depotlist'), 302)
        self.assertGet(reverse('lists-depot-overview'), 302)
        self.assertGet(reverse('lists-depot-amountoverview'), 302)
        # with access
        self.assertGet(reverse('lists-depotlist'), member=self.admin)
        self.assertGet(reverse('lists-depot-overview'), member=self.admin)
        self.assertGet(reverse('lists-depot-amountoverview'), member=self.admin)

    def test_stats(self):
        self.assertGet(reverse('mag-stats'), 302)
        self.assertGet(reverse('mag-stats'), member=self.admin)

    def test_memberlist(self):
        self.assertGet(reverse('mag-mailing-list'), 302)
        self.assertGet(reverse('mag-mailing-list'), member=self.admin)
        self.assertGet(reverse('mag-contact-list'), 302)
        self.assertGet(reverse('mag-contact-list'), member=self.admin)

    def test_subscription_export(self):
        self.assertGet(reverse('export-subscriptions'), 302)
        self.assertGet(reverse('export-subscriptions'), member=self.admin)
