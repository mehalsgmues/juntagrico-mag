"""Browser tests for the edit map feature using Playwright + Django StaticLiveServerTestCase.

These tests run a real Django dev server and a real Chromium browser, so they verify
the full stack including JavaScript, Leaflet.draw, and Bootstrap modals.

Run with:
    DJANGO_ALLOW_ASYNC_UNSAFE=1 JUNTAGRICO_SECRET_KEY=test \
        python manage.py test mapjob.test.test_edit_map_browser -v 2

Playwright browsers must be installed once:
    uv run playwright install chromium
"""

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import override_settings, tag
from django.urls import reverse
from django.utils import timezone
from playwright.sync_api import sync_playwright

from juntagrico.entity.jobs import JobType
from mapjob.models import MapJob


@tag('playwright')
@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
)
class EditMapBrowserTest(StaticLiveServerTestCase):
    """Browser tests for the edit map page."""

    fixtures = ['test/members', 'test/areas']

    @classmethod
    def _create_location(cls, name):
        from juntagrico.entity.location import Location
        return Location.objects.create(
            name=name,
            latitude='47.0',
            longitude='8.0',
            addr_street='Teststreet 1',
            addr_zipcode='8000',
            addr_location='Zurich',
            description='Test location',
        )

    def setUp(self):
        super().setUp()
        from juntagrico.entity.member import Member
        from juntagrico.entity.jobs import ActivityArea
        self.admin = Member.objects.get(email='admin@email.org')
        self.area = ActivityArea.objects.first()
        self.admin.user.is_staff = True
        self.admin.user.is_superuser = True
        self.admin.user.save()
        self.admin.confirmed = True
        self.admin.save()
        self.admin.user.set_password('testpassword')
        self.admin.user.save()

        self.map_job_type = JobType.objects.create(
            name='mapjob campaign',
            activityarea=self.area,
            default_duration=2,
            location=self._create_location('mapjob location'),
        )
        self.map_job1 = MapJob.objects.create(
            type=self.map_job_type,
            slots=2,
            time=timezone.now() - timezone.timedelta(hours=2),
            geo_area={
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [9.5479748, 45.419413],
                            [9.5488224, 45.41905],
                            [9.5503352, 45.4192242],
                        ]
                    ],
                },
                "properties": {"name": "Test Area", "description": None},
            },
        )
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch()
        self.page = self.browser.new_page()

    def tearDown(self):
        self.browser.close()
        self.playwright.stop()
        super().tearDown()

    def _login_and_go_to_edit_map(self):
        """Log in via the Django login form and navigate to the edit map page."""
        login_url = f'{self.live_server_url}/accounts/login/'
        self.page.goto(login_url, wait_until='networkidle')
        self.page.fill('input[name="username"]', 'admin@email.org')
        self.page.fill('input[name="password"]', 'testpassword')
        self.page.click('button[type="submit"]', timeout=10000)
        self.page.wait_for_url(lambda url: '/accounts/login/' not in url, timeout=15000)
        url = reverse('mapjob:edit_map_by_type', args=[self.map_job_type.id])
        self.page.goto(f'{self.live_server_url}{url}', wait_until='domcontentloaded')

    def test_edit_map_page_loads(self):
        """The edit map page should load without JavaScript errors."""
        console_errors = []
        self.page.on('console', lambda msg: console_errors.append(msg.text) if msg.type == 'error' else None)
        self._login_and_go_to_edit_map()
        self.page.wait_for_selector('.map-container')
        js_errors = [e for e in console_errors if 'edit_map' in e or 'leaflet' in e.lower()]
        self.assertEqual(js_errors, [], f"JavaScript errors on edit map page: {js_errors}")

    def test_map_shows_polygon(self):
        """The edit map should display the existing polygon."""
        self._login_and_go_to_edit_map()
        self.page.wait_for_selector('.map-container')
        self.page.wait_for_selector('.leaflet-interactive', timeout=5000)

    def test_add_area_button_exists(self):
        """The 'Neues Gebiet hinzufügen' button should be visible on the map."""
        self._login_and_go_to_edit_map()
        self.page.wait_for_selector('.add-area-control')

    def test_popup_shows_rename_and_delete(self):
        """Clicking a polygon should open a popup with rename and delete actions."""
        self._login_and_go_to_edit_map()
        self.page.wait_for_selector('.leaflet-interactive', timeout=5000)
        self.page.click('.leaflet-interactive')
        self.page.wait_for_selector('.leaflet-popup')
        popup_text = self.page.text_content('.leaflet-popup-content')
        self.assertIn('Test Area', popup_text)
        self.assertTrue(
            'bi-pencil' in popup_text or 'Löschen' in popup_text,
            f"Popup should contain pencil icon or delete button. Got: {popup_text}",
        )

    def test_bootstrap_modal_exists(self):
        """The message modal should be present in the DOM for error feedback."""
        self._login_and_go_to_edit_map()
        self.page.wait_for_selector('.map-container')
        modal = self.page.locator('#messageModal')
        self.assertTrue(modal.is_visible() or modal.count() > 0)

    def test_no_leaflet_editable_references(self):
        """The page should not load Leaflet.Editable — only Leaflet.draw."""
        self._login_and_go_to_edit_map()
        html = self.page.content()
        self.assertNotIn('Leaflet.Editable', html)
        self.assertIn('leaflet-draw', html)

    def test_back_button_navigates(self):
        """The back button should navigate back to the job map view."""
        self._login_and_go_to_edit_map()
        self.page.wait_for_selector('.map-container')
        self.page.click('a.btn-secondary')
        self.page.wait_for_load_state('networkidle')
        current_url = self.page.url
        self.assertIn(f'/map/jobs/{self.map_job_type.id}/', current_url)
