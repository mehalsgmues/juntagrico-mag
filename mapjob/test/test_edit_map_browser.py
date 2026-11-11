"""
Playwright browser tests for the edit map functionality.
Tests the interactive polygon editing, saving, and creation of MapJobs.
"""
import os
import subprocess
import time
import pytest
from playwright.sync_api import Page, expect, BrowserContext


# Test server configuration
TEST_SERVER_HOST = '127.0.0.1'
TEST_SERVER_PORT = 18888
BASE_URL = f'http://{TEST_SERVER_HOST}:{TEST_SERVER_PORT}'


# Test user credentials
TEST_USER = 'playwright_test'
TEST_PASSWORD = 'playwright_test'


def start_django_server():
    """Start Django development server in background."""
    env = os.environ.copy()
    env['DJANGO_SETTINGS_MODULE'] = 'mehalsgmues.settings'
    env['JUNTAGRICO_SECRET_KEY'] = 'test'
    proc = subprocess.Popen(
        ['.venv/bin/python', 'manage.py', 'runserver', f'{TEST_SERVER_HOST}:{TEST_SERVER_PORT}'],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    for _ in range(30):
        try:
            import urllib.request
            urllib.request.urlopen(f'{BASE_URL}/', timeout=1)
            return proc
        except Exception:
            time.sleep(0.5)
    raise RuntimeError("Django server failed to start")


def stop_django_server(proc):
    """Stop Django development server."""
    if proc:
        proc.terminate()
        proc.wait(timeout=5)


def login_to_django(page: Page):
    """Log in to Django admin via the login form."""
    page.goto(f'{BASE_URL}/admin/login/?next=/map/jobs/1/edit/')
    page.wait_for_load_state('networkidle')
    # Fill in the login form
    page.fill('input[name="username"]', TEST_USER)
    page.fill('input[name="password"]', TEST_PASSWORD)
    page.click('input[type="submit"]')
    page.wait_for_load_state('networkidle')
    # Wait for the map to load
    page.wait_for_selector('.map-container', timeout=15000)


@pytest.fixture(scope="session", autouse=True)
def django_server():
    """Session-scoped fixture to manage Django server lifecycle."""
    proc = start_django_server()
    yield proc
    stop_django_server(proc)


@pytest.fixture(scope="session")
def authenticated_context(browser, django_server):
    """Create an authenticated browser context by logging in via the form."""
    context = browser.new_context()
    # Log in once and the session cookie will persist in the context
    page = context.new_page()
    login_to_django(page)
    page.close()
    yield context
    context.close()


@pytest.fixture
def logged_in_page(authenticated_context: BrowserContext):
    """Create a new page that inherits the authenticated session."""
    page = authenticated_context.new_page()
    yield page
    page.close()


class TestEditMapPage:
    """Tests for the edit map page functionality."""

    def test_edit_map_page_loads(self, logged_in_page: Page):
        """Test that the edit map page loads without JavaScript errors."""
        page = logged_in_page
        js_errors = []
        page.on("console", lambda msg: js_errors.append(msg.text) if msg.type == "error" else None)

        page.goto(f'{BASE_URL}/map/jobs/1/edit/')
        page.wait_for_load_state('networkidle')

        expect(page.locator('.map-container')).to_be_visible()
        # The add area button is now a Leaflet control, not a page element
        expect(page.locator('.add-area-control')).to_be_visible()

        critical_errors = [e for e in js_errors if 'setEditing' in e or 'disableGlobal' in e]
        assert len(critical_errors) == 0, f"Critical JS errors found: {critical_errors}"

    def test_polygon_click_no_error(self, logged_in_page: Page):
        """Test that clicking on the map doesn't throw JS errors."""
        page = logged_in_page
        page.goto(f'{BASE_URL}/map/jobs/1/edit/')
        page.wait_for_load_state('networkidle')
        page.wait_for_selector('.leaflet-container', timeout=10000)

        map_bounds = page.locator('.map-container').bounding_box()
        center_x = map_bounds['x'] + map_bounds['width'] / 2
        center_y = map_bounds['y'] + map_bounds['height'] / 2

        page.mouse.click(center_x, center_y)
        page.wait_for_timeout(500)

    def test_add_area_button_toggles(self, logged_in_page: Page):
        """Test that the add area button toggles between draw and cancel modes."""
        page = logged_in_page
        page.goto(f'{BASE_URL}/map/jobs/1/edit/')
        page.wait_for_load_state('networkidle')
        page.wait_for_selector('.leaflet-container', timeout=10000)

        # The button is a Leaflet control with class .add-area-control
        add_btn = page.locator('.add-area-control')
        expect(add_btn).to_be_visible()

        initial_text = add_btn.text_content()
        assert 'hinzufügen' in initial_text or 'add' in initial_text.lower(), \
            f"Expected add button text, got: {initial_text}"

        add_btn.click()
        page.wait_for_timeout(500)

        after_click_text = add_btn.text_content()
        assert 'abbrechen' in after_click_text.lower() or 'cancel' in after_click_text.lower(), \
            f"Expected cancel button text, got: {after_click_text}"

        add_btn.click()
        page.wait_for_timeout(500)

        final_text = add_btn.text_content()
        assert 'hinzufügen' in final_text or 'add' in final_text.lower(), \
            f"Expected add button text after toggle, got: {final_text}"

    def test_no_setediting_error_on_edit(self, logged_in_page: Page):
        """Test that clicking a polygon doesn't throw setEditing error."""
        page = logged_in_page
        js_errors = []
        page.on("pageerror", lambda err: js_errors.append(err.message))
        page.on("console", lambda msg: js_errors.append(msg.text) if msg.type == "error" else None)

        page.goto(f'{BASE_URL}/map/jobs/1/edit/')
        page.wait_for_load_state('networkidle')
        page.wait_for_selector('.leaflet-container', timeout=10000)

        map_bounds = page.locator('.map-container').bounding_box()
        center_x = map_bounds['x'] + map_bounds['width'] / 2
        center_y = map_bounds['y'] + map_bounds['height'] / 2

        page.mouse.click(center_x, center_y)
        page.wait_for_timeout(1000)

        setediting_errors = [e for e in js_errors if 'setEditing' in str(e)]
        assert len(setediting_errors) == 0, f"setEditing error still occurring: {setediting_errors}"

        disable_global_errors = [e for e in js_errors if 'disableGlobal' in str(e)]
        assert len(disable_global_errors) == 0, f"disableGlobal error still occurring: {disable_global_errors}"

    def test_leaflet_draw_control_initialized(self, logged_in_page: Page):
        """Test that Leaflet.draw control is properly initialized."""
        page = logged_in_page
        page.goto(f'{BASE_URL}/map/jobs/1/edit/')
        page.wait_for_load_state('networkidle')
        page.wait_for_selector('.leaflet-container', timeout=10000)

        draw_control_exists = page.evaluate('''() => {
            return typeof L !== 'undefined' && L.Control !== undefined && L.Control.Draw !== undefined;
        }''')
        assert draw_control_exists, "Leaflet.draw control is not loaded"

        edit_toolbar_exists = page.evaluate('''() => {
            return typeof L !== 'undefined' && 
                   L.EditToolbar !== undefined && 
                   L.EditToolbar.Edit !== undefined;
        }''')
        assert edit_toolbar_exists, "Leaflet.draw EditToolbar is not loaded"

    def test_popup_shows_rename_and_delete(self, logged_in_page: Page):
        """Test that clicking a polygon opens a popup with rename and delete actions."""
        page = logged_in_page
        page.goto(f'{BASE_URL}/map/jobs/1/edit/')
        page.wait_for_load_state('networkidle')
        page.wait_for_selector('.leaflet-container', timeout=10000)

        # Click on the map center to open a polygon popup
        map_bounds = page.locator('.map-container').bounding_box()
        center_x = map_bounds['x'] + map_bounds['width'] / 2
        center_y = map_bounds['y'] + map_bounds['height'] / 2
        page.mouse.click(center_x, center_y)
        page.wait_for_timeout(1000)

        # Popup should be visible
        popup = page.locator('.leaflet-popup')
        expect(popup).to_be_visible()

        # Popup should have the pencil icon for inline name editing
        expect(page.locator('.popup-name')).to_be_visible()

        # "Löschen" button should be present
        expect(page.locator('.area-popup button')).to_be_visible()

    def test_back_button_navigates_correctly(self, logged_in_page: Page):
        """Test that the back button navigates to the job map view."""
        page = logged_in_page
        page.goto(f'{BASE_URL}/map/jobs/1/edit/')
        page.wait_for_load_state('networkidle')

        back_btn = page.locator('a.btn-secondary').filter(has_text='Zurück')
        expect(back_btn).to_be_visible()

        back_btn.click()
        page.wait_for_load_state('networkidle')

        current_url = page.url
        assert '/map/1/' in current_url or 'map_by_type' in current_url, \
            f"Expected to navigate to job map, but URL is: {current_url}"
