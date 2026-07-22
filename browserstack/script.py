import os
import sys

from selenium import webdriver

# Ensure the repo root is on sys.path so the 'regression' package
# resolves no matter what directory this script is launched from.
# Need this to fix issues with importing BrowserStackRun from regression directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from regression.browserstack_run import BrowserStackRun

driver = webdriver.Chrome()

# Since this script is not local (it uses the browseraudit.com production website), we don't need to prime up the
# certificate trust for cross origin domains, so we pass an empty tuple.
with BrowserStackRun(driver, cross_origins=()) as run:
    link = run.run([25]) # e.g, runs only category 25 (Cookies)
    # link = run.run() # Runs all categories
