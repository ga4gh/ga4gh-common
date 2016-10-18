"""
Emulates a Travis CI run
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys

import ga4gh_common
import ga4gh_common.utils as utils


class TravisSimulator(object):

    logStrPrefix = '***'
    yamlFileLocation = '.travis.yml'

    def parseTestCommands(self):
        yamlData = utils.getYamlDocument(self.yamlFileLocation)
        return yamlData['script']

    def runTests(self):
        testCommands = self.parseTestCommands()
        for command in testCommands:
            self.log('Running: "{}"'.format(command))
            utils.runCommand(command)
        self.log('SUCCESS')

    def log(self, logStr):
        utils.log("{0} {1}".format(self.logStrPrefix, logStr))


def run_tests_main():
    if len(sys.argv) >= 2 and sys.argv[1] == '--version':
        utils.log("GA4GH run_tests version {}".format(
            ga4gh_common.__version__))
        return
    travisSimulator = TravisSimulator()
    travisSimulator.runTests()
