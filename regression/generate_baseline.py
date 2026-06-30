from selenium import webdriver

from common import generate_browser_key, extract_id_and_passkey, fetch_results, store_baseline
from browserstack_run import BrowserStackRun

driver = webdriver.Chrome()

with BrowserStackRun(driver) as run:
    link = run.run()
    id, passkey = extract_id_and_passkey(link)
    results = fetch_results(id, passkey)

    # Writes the baseline results as a json file
    key = generate_browser_key(driver)
    store_baseline(key, results)
    print(f"Created baseline file for browser key={key}")
