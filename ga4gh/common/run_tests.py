"""
Emulates a Travis CI run
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import ga4gh.common
import ga4gh.common.cli as cli
import ga4gh.common.utils as utils


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
    parser = cli.createArgumentParser("runs tests for a ga4gh package")
    versionString = "GA4GH Runtests Version {}".format(
        ga4gh.common.__version__)
    parser.add_argument(
        "--version", version=versionString, action="version")
    parser.parse_args()

    travisSimulator = TravisSimulator()
    travisSimulator.runTests()
