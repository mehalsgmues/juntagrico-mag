from django.urls import reverse
from juntagrico.tests import JuntagricoTestCase


class MagTests(JuntagricoTestCase):
    def test_template_override(self):
        self.assertGet(reverse('home'), member=self.admin)
        self.assertGet(reverse('jobs'), member=self.admin)

    def test_stats(self):
        self.assertGet(reverse('mag-stats'), 302, self.member2)
        self.assertGet(reverse('mag-stats'), member=self.admin)
        self.assertGet(reverse('mag-stats-export'), 302, self.member2)
        self.assertGet(reverse('mag-stats-export'), member=self.admin)

    def test_api(self):
        self.assertGet(reverse('mag-mailing-list'), 302, self.member2)
        self.assertGet(reverse('mag-mailing-list'), member=self.admin)
        self.assertGet(reverse('mag-contact-list'), 302, self.member2)
        self.assertGet(reverse('mag-contact-list'), member=self.admin)

    def test_memberlist(self):
        self.assertGet(reverse('mag-mailing-list'), 302, self.member2)
        self.assertGet(reverse('mag-mailing-list'), member=self.admin)
        self.assertGet(reverse('mag-contact-list'), 302, self.member2)
        self.assertGet(reverse('mag-contact-list'), member=self.admin)
        self.assertGet(reverse('manage-member-active'), 403, self.member2)
        self.assertGet(reverse('manage-member-active'), member=self.admin)

    def test_subscription_export(self):
        self.assertGet(reverse('export-subscriptions-mag'), 302, self.member2)
        self.assertGet(reverse('export-subscriptions-mag'), member=self.admin)

    def test_job_admin(self):
        self.assertGet(reverse('admin:action-mass-copy-job', args=[self.job1.id]), member=self.admin)
