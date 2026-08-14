from copy import deepcopy

from django.conf import settings
from django.core.files.base import ContentFile
from django.test import override_settings
from django.urls import reverse
from juntagrico.tests import JuntagricoTestCase


class InvalidTemplateVariable(str):
    def __mod__(self, other):
        raise NameError(f"In template, undefined variable or unknown value for: '{other}'")


@override_settings(STORAGES={
    'internal': {'BACKEND': 'django.core.files.storage.InMemoryStorage'},
    'staticfiles': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
})
class DepotListTests(JuntagricoTestCase):
    def setUp(self):
        super().setUp()
        from juntagrico.util.pdf import internal_storage
        self.internal_storage = internal_storage
        self.internal_storage.delete('depotlist.pdf')
        self.internal_storage.delete('depot_overview.pdf')
        self.internal_storage.delete('amount_overview.pdf')

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

    def assertListsCreated(self):
        self.assertTrue(self.internal_storage.exists('depotlist.pdf'))
        self.assertTrue(self.internal_storage.exists('depot_overview.pdf'))
        self.assertTrue(self.internal_storage.exists('amount_overview.pdf'))

    def testManualDepotListGeneration(self):
        url = reverse('lists')
        data = {
            'for_date': '2025-12-31',
            'future': False,
            'submit': 'yes',
        }
        # member has no access
        self.assertPost(url, data, code=200)
        self.assertFalse(self.internal_storage.exists('depotlist.pdf'))
        # admin has access
        self.assertPost(url, data, code=302, member=self.admin)
        self.assertListsCreated()


@override_settings(STORAGES={
    'internal': {'BACKEND': 'django.core.files.storage.InMemoryStorage'},
    'staticfiles': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
})
class DepotListAccessTests(JuntagricoTestCase):
    def setUp(self):
        super().setUp()
        from juntagrico.util.pdf import internal_storage
        self.internal_storage = internal_storage
        # create empty dummy files
        self.internal_storage.save('depotlist.pdf', ContentFile(''))
        self.internal_storage.save('depot_overview.pdf', ContentFile(''))
        self.internal_storage.save('amount_overview.pdf', ContentFile(''))

    def testViewDepotList(self):
        url = reverse('lists')
        self.assertGet(url)
        self.assertGet(url, member=self.member2, code=302)

    def testDownloadDepotList(self):
        for depot_list in ['depotlist', 'depot_overview', 'amount_overview']:
            url = reverse('lists-download', args=[depot_list])
            self.assertGet(url)
            self.assertGet(url, member=self.member2, code=302)
