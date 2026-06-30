import json

from selenium.common import (
    NoSuchElementException,
    NoSuchFrameException,
    StaleElementReferenceException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = "https://browseraudit.com"

# These are all the cross-origin domains the test suite sends requests to.
# We need to enable acceptInsecureCerts in browserstack.yml so that the browserstack VM
# trusts the self signed BrowserAudit certificate on the local website.
# This works only for the domain the selenium driver accesses (the base URL), but not
# on cross origin domains during the test run. So we need to load all of the other domains
# with driver.get() so they are all trusted by the browser before we start the test execution
CROSS_ORIGINS = (
    "https://test.browseraudit.com",
    "https://browseraudit.org",
    "https://test.browseraudit.org",
)

# Suite running constantly creates/destroys iframes in the sandbox, need to ignore these transient errors
IGNORED_EXCEPTIONS = (
    NoSuchElementException,
    NoSuchFrameException,
    StaleElementReferenceException,
)

class BrowserStackRun:

    def __init__(self, driver, timeout=400):
        self.driver = driver
        self.timeout = timeout

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        # The session succeeded if the suite ran without raising
        passed = exc_type is None
        self.set_session_status(
            passed,
            "Test suite completed and results link retrieved"
            if passed
            else "Test suite did not complete or results link was not found",
        )
        self.driver.quit()
        return False

    def prime_cross_origin_certs(self):
        for origin in CROSS_ORIGINS:
            self.driver.get(origin)

    def select_categories(self, category_ids=None):
        """Select which test categories to run. None runs the full suite"""
        if category_ids is None:
            return

        # Expand the category selection panel
        self._wait_clickable(
            "#main > div > div.panel-group > div:nth-child(1)"
            " > div.panel-heading > h2 > a"
        ).click()

        # Deselect everything, then pick the requested categories
        self._wait_clickable(
            "#browseraudit-categories > table > tbody > tr:nth-child(1)"
            " > td > div > button:nth-child(2)"
        ).click()

        for category_id in category_ids:
            self._wait_clickable(f"#browseraudit-selected-{category_id}").click()

    def start(self):
        print("Clicking the Test Me button")
        self._wait_clickable(
            ".btn.btn-primary.btn-lg.browseraudit-start"
        ).click()

    def wait_for_report_link(self) -> str:
        # Poll the top-level document, ignore transient iframes to avoid an exception ending the run
        self.driver.switch_to.default_content()
        link = WebDriverWait(
            self.driver,
            self.timeout,
            ignored_exceptions=IGNORED_EXCEPTIONS,
        ).until(
            EC.presence_of_element_located(
                (By.PARTIAL_LINK_TEXT, "permanent link")
            )
        )
        href = link.get_attribute("href")
        print("Test Report Link:", href)
        return href

    def run(self, category_ids=None) -> str:
        """Drive a full run and return the permanent results link"""
        self.prime_cross_origin_certs()
        self.driver.get(BASE_URL)
        self.select_categories(category_ids)
        self.start()
        return self.wait_for_report_link()

    def set_session_status(self, passed: bool, reason: str):
        executor_object = {
            "action": "setSessionStatus",
            "arguments": {
                "status": "passed" if passed else "failed",
                "reason": reason,
            },
        }
        self.driver.execute_script(
            "browserstack_executor: {}".format(json.dumps(executor_object))
        )

    def _wait_clickable(self, css_selector, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))
        )
