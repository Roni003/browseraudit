import re

def extract_id_and_passkey(test_report_link: str):
    split = test_report_link.split("/")
    assert len(split) == 6 # Make sure we have the expected url format
    passkey = split[-1]
    id = split[-2]
    return id, passkey

def _slug(s):
    return re.sub(r"[^a-z0-9]+", "-", str(s).strip().lower()).strip("-")

def browser_key(driver, version_parts=2):
    caps = driver.capabilities
    name = caps.get("browserName", "unknown")
    version = caps.get("browserVersion") or caps.get("version") or "0"
    platform = caps.get("platformName") or caps.get("platform") or "unknown"

    # Truncate version to N components so auto-updating browsers
    # (Chrome "120.0.6099.109") don't invalidate the baseline every patch.
    version = ".".join(version.split(".")[:version_parts])

    return f"{_slug(name)}-{_slug(platform)}-{_slug(version)}"