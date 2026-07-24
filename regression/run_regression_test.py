import regression_helpers
import common
from selenium import webdriver
from browserstack_run import BrowserStackRun, CategoryId

driver = webdriver.Chrome()

with BrowserStackRun(driver) as run:
    # link = run.run([CategoryId.COOKIES.value]) # e.g, only run the test against a specific category (executes a lot faster)
    link = run.run()
    id, passkey = common.extract_id_and_passkey(link)
    current = common.fetch_results(id, passkey)
    baseline = regression_helpers.parse_baseline(common.generate_browser_key())
    ok = regression_helpers.compare_results(baseline, current)