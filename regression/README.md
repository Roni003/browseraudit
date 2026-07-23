# Regression testing for BrowserAudit

This project uses BrowserStack to automatically run the BrowserAudit test suite on multiple browsers on cloud VMs. 
This is done to compare the test results from different versions of BrowserAudit to ensure that the results are 
consistent and to catch any regressions in the codebase. This should be done after any changes are made to the 
BrowserAudit codebase locally, before pushing the changes to the production server.

## Requirements

- In order to run automatic tests, you need to have a [BrowserStack](https://www.browserstack.com/) account.
- You need `python` to run the tests (tested on Python 3.12.3).
- Install requirements: `pip install -r requirements.txt`

## Configure

- Copy `browserstack.yml-dist` to `browserstack.yml`
- Copy `userName` and `accessKey` key from [https://www.browserstack.com/accounts/settings](https://www.browserstack.com/accounts/settings) to `browserstack.yml`
- Additional information on configuring `browserstack.yml` can be found here: https://www.browserstack.com/docs/
- Ensure that you are currently running the BrowserAudit server locally (consult the README in the root directory), as the tests will be run against your local instance of BrowserAudit, not the production server. 
This means any changes you make to the BrowserAudit codebase locally will be reflected in the test results.
- Navigate into the `/regression` directory before executing the following commands.

## Baselines
A baseline is a snapshot of test results and metadata for a test suite execution on a specific platform and browser. 
The `/baselines/` directory already contains the baselines from previous executions on multiple platforms. You can either use
an existing baseline or create a new one. To create a baseline,
Choose the specific platform and browser you want to create a baseline for, then put the platform information in the 
`browserstack.yml` file. After that, run the command `browserstack-sdk python3 ./generate_baseline.py`.

## Testing
To run a regression test against a specific baseline, choose the specific platform and browser you want to test against, 
then put the platform information in the `browserstack.yml` file, the platform information of a baseline can be found in the
`platformInfoYaml` field in the json file. After that, run the command 
`browserstack-sdk python3 ./run_regression_test.py`. The test results will be compared against the baseline 
and any differences in test results will be reported in the output. You can run multiple platforms at the same time as long as a 
baseline exists for each platform. If a baseline does not exist for a specific platform, you will need to create one first before running the regression test.