"""
Shim for running the run_tests program during development
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import ga4gh_common.run_tests as run_tests


if __name__ == '__main__':
    run_tests.run_tests_main()
