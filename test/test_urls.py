from django.urls import reverse

from test import MagTestCase


class MagTests(MagTestCase):

    def test_template_override(self):
        self.assertGet(reverse('home'), member=self.admin)
        self.assertGet(reverse('jobs'), member=self.admin)

    def test_depolist(self):
        # without access
        self.assertGet(reverse('lists-mgmt'), 302)
        self.assertGet(reverse('lists-mgmt-success'), 302)
        self.assertGet(reverse('lists-generate'), 302)
        self.assertGet(reverse('lists-generate-future'), 302)
        self.assertGet(reverse('lists-depotlist'), 302)
        self.assertGet(reverse('lists-depot-overview'), 302)
        self.assertGet(reverse('lists-depot-amountoverview'), 302)
        # with access
        self.assertGet(reverse('lists-mgmt'), member=self.admin)
        self.assertGet(reverse('lists-mgmt-success'), member=self.admin)
        self.assertGet(reverse('lists-generate'), 302, member=self.admin)
        self.assertGet(reverse('lists-generate-future'), 302, member=self.admin)
        self.assertGet(reverse('lists-depotlist'), member=self.admin)
        self.assertGet(reverse('lists-depot-overview'), member=self.admin)
        self.assertGet(reverse('lists-depot-amountoverview'), member=self.admin)

    def test_stats(self):
        self.assertGet(reverse('mag-stats'), 302)
        self.assertGet(reverse('mag-stats'), member=self.admin)
        self.assertGet(reverse('mag-stats-export'), 302)
        self.assertGet(reverse('mag-stats-export'), member=self.admin)

    def test_api(self):
        self.assertGet(reverse('mag-mailing-list'), 302)
        self.assertGet(reverse('mag-mailing-list'), member=self.admin)
        self.assertGet(reverse('mag-contact-list'), 302)
        self.assertGet(reverse('mag-contact-list'), member=self.admin)
        self.assertGet(reverse('shares-preview'), 302)
        self.assertGet(reverse('shares-preview'), member=self.admin)

    def test_memberlist(self):
        self.assertGet(reverse('mag-mailing-list'), 302)
        self.assertGet(reverse('mag-mailing-list'), member=self.admin)
        self.assertGet(reverse('mag-contact-list'), 302)
        self.assertGet(reverse('mag-contact-list'), member=self.admin)

    def test_subscription_export(self):
        self.assertGet(reverse('export-subscriptions-mag'), 302)
        self.assertGet(reverse('export-subscriptions-mag'), member=self.admin)

    def test_job_admin(self):
        self.assertGet(reverse('admin:action-mass-copy-job', args=[self.job1.id]), member=self.admin)
