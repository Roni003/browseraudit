import json
import os
import re
from dataclasses import dataclass

import requests
from browserstack_sdk import BrowserStackSdk

URL_BASE = "https://browseraudit.com"
BASELINE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "baselines")

@dataclass
class Result:
    browser_audit_version: str
    test_results: dict[str, str]

    @classmethod
    def from_dict(cls, data: dict) -> "Result":
        return cls(
            browser_audit_version=data["browserAuditVersion"],
            test_results=data["testResults"],
        )

def fetch_results(id: str | int, passkey: str) -> Result:
    url = URL_BASE + "/suite_execution/json/" + str(id) + "/" + str(passkey)
    req = requests.get(url, verify=False) # Need to set verify to false to allow the self signed certificate
    body = req.json()
    results = {tid: r["outcome"] for tid, r in body["testResults"].items()}
    browser_audit_version = body["browserAuditVersion"]
    return Result(browser_audit_version, results)

def extract_id_and_passkey(test_report_link: str):
    split = test_report_link.split("/")
    assert len(split) == 6 # Make sure we have the expected url format
    passkey = split[-1]
    id = split[-2]
    return id, passkey

def _slug(s):
    return re.sub(r"[^a-z0-9]+", "-", str(s).strip().lower()).strip("-")

def generate_browser_key():
    platform = BrowserStackSdk.get_current_platform()
    out = f""

    for key, val in platform.items():
        # Truncate version to N components so auto-updating browsers
        # (Chrome "120.0.6099.109") don't invalidate the baseline every patch.
        if key == "version":
            val = ".".join(val.split(".")[:2])

        out += _slug(val) + "-"

    return out.removesuffix("-")

def store_baseline(browser_key: str, result: Result):
    os.makedirs(BASELINE_DIR, exist_ok=True)
    path = os.path.join(BASELINE_DIR, browser_key + ".json")
    with open(path, 'w') as f:
        out = {
            "browserKey": browser_key,
            "browserAuditVersion": result.browser_audit_version,
            "testResults": result.test_results
        }
        json.dump(out, f, indent=2)