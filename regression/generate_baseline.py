# Generates the baseline expected test results for a given browser version
import json
from selenium import webdriver
from selenium.common import NoSuchFrameException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from common import generate_browser_key, extract_id_and_passkey, fetch_results, store_baseline

# Launch the browser and navigate to BrowserAudit.com
driver = webdriver.Chrome() # Driver will be overwritten by BrowserStack config file

# Prime a per-origin TLS exception for each cross-origin test domain.
# safaridriver ignores acceptInsecureCerts globally, so without visiting these
# first the suite's cross-origin requests are blocked and it hangs on startup.
for origin in ["https://test.browseraudit.com", "https://browseraudit.org", "https://test.browseraudit.org"]:
    driver.get(origin)

driver.get("https://browseraudit.com")

categories_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, '#main > div > div.panel-group > div:nth-child(1) > div.panel-heading > h2 > a'))
)

categories_button.click()

none_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR,
                                '#browseraudit-categories > table > tbody > tr:nth-child(1) > td > div > button:nth-child(2)'))
)

none_button.click()

cookies_selector = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR,
                                '#browseraudit-selected-25'))
)

cookies_selector.click()

# Find and click the "Test Me" button
test_me_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, '.btn.btn-primary.btn-lg.browseraudit-start'))
)

print('Clicking the Test Me button')

test_me_button.click()
test_report_link = ""

try:
    # Make sure we're polling the top-level document, not a transient test
    # iframe that the suite may have left the context pointing at.
    driver.switch_to.default_content()

    # Wait until the test results link appears. The test suite running can cause
    # issues with the safari driver so we need to handle those exceptions
    # Treat those as transient and keep polling instead of failing the run.
    test_results_link = WebDriverWait(
        driver,
        15,
        ignored_exceptions=(
            NoSuchElementException,
            NoSuchFrameException,
            StaleElementReferenceException,
        ),
    ).until(
        EC.presence_of_element_located(
            (By.PARTIAL_LINK_TEXT, "permanent link")
        )
    )

    # Get the href attribute of the test results link
    test_report_link = test_results_link.get_attribute('href')

    # Print the test report link for review
    print('Test Report Link:', test_report_link)

    # Set the status of the session to "passed" if link retrieved successfuly
    if ("result" in test_report_link):
        executor_object = {
            'action': 'setSessionStatus',
            'arguments': {
                'status': "passed",
                'reason': "Test suite completed and results link retrieved"
            }
        }
        browserstack_executor = 'browserstack_executor: {}'.format(json.dumps(executor_object))
        driver.execute_script(browserstack_executor)
except Exception as e:
    # Mark the session as failed so it shows up correctly on the dashboard
    print('Test suite failed:', e)
    executor_object = {
        'action': 'setSessionStatus',
        'arguments': {
            'status': "failed",
            'reason': "Test suite did not complete or results link was not found"
        }
    }
    browserstack_executor = 'browserstack_executor: {}'.format(json.dumps(executor_object))
    driver.execute_script(browserstack_executor)
finally:
    # Write the baseline
    if not isinstance(test_report_link, str) or not test_report_link.strip():
        print("Failed to get test report link")
    else:
        key = generate_browser_key(driver)
        run_id, passkey = extract_id_and_passkey(test_report_link)
        results = fetch_results(run_id, passkey)
        store_baseline(key, results)

    # Close the browser
    driver.quit()
