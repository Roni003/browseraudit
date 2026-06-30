import regression_helpers
import common
from selenium import webdriver
from browserstack_run import BrowserStackRun

driver = webdriver.Chrome()

with BrowserStackRun(driver) as run:
    link = run.run()
    id, passkey = common.extract_id_and_passkey(link)
    current = common.fetch_results(id, passkey)
    baseline = regression_helpers.parse_baseline(common.generate_browser_key())
    ok = regression_helpers.compare_results(driver, baseline, current)