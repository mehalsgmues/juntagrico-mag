from copy import deepcopy

from django.conf import settings
from django.core.files.storage import default_storage
from django.test import override_settings
from django.urls import reverse
from juntagrico.tests import JuntagricoTestCase


class InvalidTemplateVariable(str):
    def __mod__(self, other):
        raise NameError(f"In template, undefined variable or unknown value for: '{other}'")


@override_settings(STORAGES={
    'default': {'BACKEND': 'django.core.files.storage.InMemoryStorage'},
    'staticfiles': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
})
class DepotListTests(JuntagricoTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Modify settings for test
        template_setting = deepcopy(settings.TEMPLATES)
        template_setting[0]['OPTIONS']['string_if_invalid'] = InvalidTemplateVariable('%s')
        cls.override = override_settings(TEMPLATES=template_setting)
        cls.override.enable()  # Activate the override

    @classmethod
    def tearDownClass(cls):
        cls.override.disable()  # Restore settings
        super().tearDownClass()

    def tearDown(self):
        default_storage.delete('depotlist.pdf')
        default_storage.delete('depot_overview.pdf')
        default_storage.delete('amount_overview.pdf')

    def assertListsCreated(self):
        self.assertTrue(default_storage.exists('depotlist.pdf'))
        self.assertTrue(default_storage.exists('depot_overview.pdf'))
        self.assertTrue(default_storage.exists('amount_overview.pdf'))

    def testManualDepotListGeneration(self):
        url = reverse('lists')
        data = {
            'for_date': '2025-12-31',
            'future': False,
            'submit': 'yes',
        }
        # member has no access
        self.assertPost(url, data, code=200)
        self.assertFalse(default_storage.exists('depotlist.pdf'))
        # admin has access
        self.assertPost(url, data, code=302, member=self.admin)
        self.assertListsCreated()


class DepotListAccessTests(JuntagricoTestCase):
    def testViewDepotList(self):
        url = reverse('lists')
        self.assertGet(url)
        self.assertGet(url, member=self.member2, code=302)

    def testDownloadDepotList(self):
        for depot_list in ['depotlist', 'depot_overview', 'amount_overview']:
            url = reverse('lists-download', args=[depot_list])
            self.assertGet(url)
            self.assertGet(url, member=self.member2, code=302)
