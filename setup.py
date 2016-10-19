# Don't import __future__ packages here; they make setup fail

import ga4gh_common.setup as setup


packageDict = {
    "name": "ga4gh_common",
    "description": "Common utilities for GA4GH packages",
    "packages": ["ga4gh_common"],
    "url": "https://github.com/ga4gh/ga4gh-common",
    "use_scm_version": { "write_to": "ga4gh_common/_version.py" },
    "entry_points": {
        "console_scripts": [
            "ga4gh_run_tests=ga4gh_common.run_tests:run_tests_main",
        ],
    },
}
setup.doSetup(packageDict)
