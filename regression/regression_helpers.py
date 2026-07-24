import json
import os.path

from common import Result, BASELINE_DIR, generate_browser_key

# List of test IDs that have unreliable results (mostly due to async result reporting causing flaky
# results when reading the test), therefore shouldn't be included in the regression check
UNRELIABLE_TEST_IDS = [
    237, 361, 362, 363, 364, 365, 366, 369, 372, 391, 393, 459, 461, 464
]

def parse_baseline(browser_key: str) -> Result:
    path = os.path.join(BASELINE_DIR, browser_key + ".json")
    if not os.path.exists(path):
        raise Exception("Baseline does not exist for browser key: " + browser_key)

    with open(path, "r") as file:
        data = json.load(file)
        return Result.from_dict(data)

def compare_results(baseline: Result, current: Result) -> bool:
    failed = _diff_test_results(baseline, current)
    browser_key = generate_browser_key()
    if len(failed) == 0:
        print(f"--- Passed regression test ({browser_key}) ---")
        return True
    else:
        print(f"--- Failed regression test ({browser_key}), {len(failed)} tests failed ---")
        for test in failed:
            print(test)
        return False

def _diff_test_results(baseline: Result, current: Result) -> list[dict]:
    baseline_results = baseline.test_results
    current_results = current.test_results
    failed_tests = []
    for key, val in baseline_results.items():
        if int(key) in UNRELIABLE_TEST_IDS:
            continue
        if key not in current_results:
            continue

        baseline_result = baseline_results[key]
        current_result = current_results[key]
        if baseline_result == current_result:
            continue

        failed_tests.append({
            "test_id": key,
            "expected": baseline_result,
            "got": current_result
        })

    return failed_tests