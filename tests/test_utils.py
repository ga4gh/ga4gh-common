"""
Tests for common utilities
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import mock
import tempfile
import subprocess
import unittest
import sys

import ga4gh_common.utils as utils


class AbstractTestUtils(unittest.TestCase):
    """
    Base class for tests that contains common attributes
    """
    executables = ['ls', 'rm']
    nonexistentExecutable = 'doesNotExistAsAnExecutable'
    validCommand = 'echo -n'
    invalidCommand = 'ls -5'


class TestUtils(AbstractTestUtils):

    def testGetPathOfExecutable(self):
        path = utils.getPathOfExecutable(self.executables[0])
        self.assertIsNotNone(path)
        notFoundPath = utils.getPathOfExecutable(self.nonexistentExecutable)
        self.assertIsNone(notFoundPath)

    def testRunCommand(self):
        utils.runCommand(self.validCommand)
        with self.assertRaises(subprocess.CalledProcessError):
            utils.runCommand(self.invalidCommand, silent=True)
        with self.assertRaises(Exception):
            utils.runCommand(self.nonexistentExecutable, silent=True)

    def testRunCommandSplits(self):
        utils.runCommandSplits(self.validCommand.split())
        with self.assertRaises(subprocess.CalledProcessError):
            utils.runCommandSplits(self.invalidCommand.split(), silent=True)
        with self.assertRaises(Exception):
            utils.runCommand([self.nonexistentExecutable], silent=True)

    def testGetYamlDocument(self):
        yamlText = """
provider:
        key: aKey
        """
        handle, path = tempfile.mkstemp()
        with open(path, 'w') as yamlFile:
            yamlFile.write(yamlText)
        doc = utils.getYamlDocument(path)
        self.assertEqual(doc, {'provider': {'key': 'aKey'}})

    def testZipLists(self):
        a = [1, 2]
        b = [3, 4]
        c = [5, 6]
        d = [7, 8, 9]
        e = [10]
        result = utils.zipLists(a, b, c)
        self.assertEqual(result, [(1, 3, 5), (2, 4, 6)])
        with self.assertRaises(AssertionError):
            utils.zipLists(c, d)
        with self.assertRaises(AssertionError):
            utils.zipLists(d, e)

    def testGetLinesFromLogFile(self):
        handle, path = tempfile.mkstemp()
        message = 'aMessage'
        with open(path, 'w') as yamlFile:
            yamlFile.write(message)
        with open(path) as readFile:
            result = utils.getLinesFromLogFile(readFile)
        self.assertEqual(result, [message])

    def testPowerset(self):
        s = [1, 2, 3]
        expected = [
            (), (1, ), (2, ), (3, ), (1, 2), (1, 3), (2, 3), (1, 2, 3)]
        result = list(utils.powerset(s))
        self.assertEqual(result, expected)

    def testRepeat(self):
        aList = []

        @utils.Repeat()
        def repeatFunc():
            aList.append(1)
            return len(aList) < 3
        repeatFunc()
        self.assertEqual(aList, [1, 1, 1])

    def testTimeout(self):

        @utils.Timeout(1)
        def timeoutFunc():
            while True:
                pass
        with self.assertRaises(utils.TimeoutException):
            timeoutFunc()

    def testSuppressOutput(self):
        # not really sure how to test this
        with utils.suppressOutput():
            pass


class TestUtilsPrintMocked(AbstractTestUtils):
    """
    Tests that need to have print output suppressed
    """
    printMock = mock.Mock()

    def setUp(self):
        self.printMock.reset_mock()

    @mock.patch('__builtin__.print', printMock)
    def testTimed(self):
        aList = []

        @utils.Timed()
        def timedFunc():
            aList.append(1)
        timedFunc()
        self.assertEquals(aList, [1])
        self.assertEquals(self.printMock.call_count, 1)

    @mock.patch('__builtin__.print', printMock)
    def testLog(self):
        utils.log("message")
        self.assertEquals(self.printMock.call_count, 1)

    @mock.patch('__builtin__.print', printMock)
    def testRequireExecutables(self):
        utils.requireExecutables(self.executables)
        with self.assertRaises(SystemExit):
            utils.requireExecutables([self.nonexistentExecutable])
        self.assertEquals(self.printMock.call_count, 2)


class TestCaptureOutput(unittest.TestCase):
    """
    Test that the captureOutput correctly returns the value of stdout
    and stderr for a function.
    """

    def testCapture(self):
        stdoutValue = "stdout"
        stderrValue = "stderr"

        def func():
            print(stdoutValue, file=sys.stdout, end="")
            print(stderrValue, file=sys.stderr, end="")
        stdout, stderr = utils.captureOutput(func)
        self.assertEqual(stdout, stdoutValue)
        self.assertEqual(stderr, stderrValue)

        # Empty stdout
        def func():
            print(stderrValue, file=sys.stderr, end="")
        stdout, stderr = utils.captureOutput(func)
        self.assertEqual(stdout, "")
        self.assertEqual(stderr, stderrValue)

        # Empty stderr
        def func():
            print(stdoutValue, file=sys.stdout, end="")
        stdout, stderr = utils.captureOutput(func)
        self.assertEqual(stdout, stdoutValue)
        self.assertEqual(stderr, "")

    def testArgs(self):
        def func(one, two, three, keywordOne=None, keywordTwo=None):
            print(one, two, three, keywordOne, keywordTwo, file=sys.stdout)
        stdout, stderr = utils.captureOutput(
            func, "1", "2", "3", keywordTwo="5", keywordOne="4")
        self.assertEqual(stdout, "1 2 3 4 5\n")
        self.assertEqual(stderr, "")
