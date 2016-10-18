"""
Utilities used across many GA4GH packages
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import StringIO
import contextlib
import functools
import humanize
import itertools
import os
import shlex
import signal
import subprocess
import sys
import time
import yaml


packageName = 'ga4gh'


def log(message):
    """
    Log a message
    """
    print(message)


def getPathOfExecutable(executable):
    """
    Returns the full path of the executable, or None if the executable
    can not be found.
    """
    exe_paths = os.environ['PATH'].split(':')
    for exe_path in exe_paths:
        exe_file = os.path.join(exe_path, executable)
        if os.path.isfile(exe_file) and os.access(exe_file, os.X_OK):
            return exe_file
    return None


def requireExecutables(executables):
    """
    Check that all of the given executables are on the path.
    If at least one of them is not, exit the script and inform
    the user of the missing requirement(s).
    """
    missingExecutables = []
    for executable in executables:
        if getPathOfExecutable(executable) is None:
            missingExecutables.append(executable)
    if len(missingExecutables) > 0:
        log("In order to run this script, the following "
            "executables need to be on the path:")
        for missingExecutable in missingExecutables:
            log(missingExecutable)
        exit(1)


def ga4ghImportGlue():
    """
    Call this method before importing a ga4gh module in the scripts dir.
    Otherwise, you will be using the installed package instead of
    the development package.
    Assumes a certain directory structure.
    """
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(path)


def runCommand(command, silent=False):
    """
    Run a shell command
    """
    splits = shlex.split(command)
    runCommandSplits(splits, silent=silent)


def runCommandSplits(splits, silent=False):
    """
    Run a shell command given the command's parsed command line
    """
    try:
        if silent:
            with open(os.devnull, 'w') as devnull:
                subprocess.check_call(splits, stdout=devnull, stderr=devnull)
        else:
            subprocess.check_call(splits)
    except OSError, e:
        if e.errno == 2:  # cmd not found
            raise Exception(
                "Can't find command while trying to run {}".format(splits))
        else:
            raise


def getAuthValues(filePath='scripts/auth.yml'):
    """
    Return the script authentication file as a dictionary
    """
    return getYamlDocument(filePath)


def getYamlDocument(filePath):
    """
    Return a yaml file's contents as a dictionary
    """
    with open(filePath) as stream:
        doc = yaml.load(stream)
        return doc


def captureOutput(func, *args, **kwargs):
    """
    Runs the specified function and arguments, and returns the
    tuple (stdout, stderr) as strings.
    """
    stdout = sys.stdout
    sys.stdout = StringIO.StringIO()
    stderr = sys.stderr
    sys.stderr = StringIO.StringIO()
    try:
        func(*args, **kwargs)
        stdoutOutput = sys.stdout.getvalue()
        stderrOutput = sys.stderr.getvalue()
    finally:
        sys.stdout.close()
        sys.stdout = stdout
        sys.stderr.close()
        sys.stderr = stderr
    return stdoutOutput, stderrOutput


def zipLists(*lists):
    """
    Checks to see if all of the lists are the same length, and throws
    an AssertionError otherwise.  Returns the zipped lists.
    """
    length = len(lists[0])
    for i, list_ in enumerate(lists[1:]):
        if len(list_) != length:
            msg = "List at index {} has length {} != {}".format(
                i + 1, len(list_), length)
            raise AssertionError(msg)
    return zip(*lists)


def getLinesFromLogFile(stream):
    stream.flush()
    stream.seek(0)
    lines = stream.readlines()
    return lines


def getProjectRootFilePath():
    # assumes we're in a directory one level below the project root
    return os.path.dirname(os.path.dirname(__file__))


def getGa4ghFilePath():
    return os.path.join(getProjectRootFilePath(), packageName)


def powerset(iterable, maxSets=None):
    """
    powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)

    See https://docs.python.org/2/library/itertools.html#recipes
    """
    s = list(iterable)
    return itertools.islice(itertools.chain.from_iterable(
        itertools.combinations(s, r) for r in range(len(s) + 1)),
        0, maxSets)


# ---------------- Decorators ----------------


class TimeoutException(Exception):
    """
    A process has taken too long to execute
    """


class Timed(object):
    """
    Decorator that times a method, reporting runtime at finish
    """
    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self.start = time.time()
            result = func(*args, **kwargs)
            self.end = time.time()
            self._report()
            return result
        return wrapper

    def _report(self):
        delta = self.end - self.start
        timeString = humanize.time.naturaldelta(delta)
        log("Finished in {} ({:.2f} seconds)".format(timeString, delta))


class Repeat(object):
    """
    A decorator to use for repeating a tagged function.
    The tagged function should return true if it wants to run again,
    and false if it wants to stop repeating.
    """
    defaultSleepSeconds = 0.1

    def __init__(self, sleepSeconds=defaultSleepSeconds):
        self.sleepSeconds = sleepSeconds

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            while func(*args, **kwargs):
                time.sleep(self.sleepSeconds)
        return wrapper


class Timeout(object):
    """
    A decorator to use for only allowing a function to run
    for a limited amount of time
    """
    defaultTimeoutSeconds = 60

    def __init__(self, timeoutSeconds=defaultTimeoutSeconds):
        self.timeoutSeconds = timeoutSeconds

    def __call__(self, func):

        def _handle_timeout(signum, frame):
            raise TimeoutException()

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # set the alarm and execute func
                signal.signal(signal.SIGALRM, _handle_timeout)
                signal.alarm(self.timeoutSeconds)
                result = func(*args, **kwargs)
            finally:
                # clear the alarm
                signal.alarm(0)
            return result
        return wrapper


# ---------------- Context managers ----------------


@contextlib.contextmanager
def suppressOutput():
    # I would like to use sys.stdout.fileno() and sys.stderr.fileno()
    # here instead of literal fd numbers, but nose does something like
    # sys.stdout = StringIO.StringIO() when the -s flag is not enabled
    # (to capture test output so it doesn't get entangled with nose's
    # display) so the sys.stdout and sys.stderr objects are not able to
    # be accessed here.
    try:
        # redirect stdout and stderr to /dev/null
        devnull = open(os.devnull, 'w')
        origStdoutFd = 1
        origStderrFd = 2
        origStdout = os.dup(origStdoutFd)
        origStderr = os.dup(origStderrFd)
        sys.stdout.flush()
        sys.stderr.flush()
        os.dup2(devnull.fileno(), origStdoutFd)
        os.dup2(devnull.fileno(), origStderrFd)
        # enter the wrapped code
        yield
    finally:
        # restore original file streams
        devnull.flush()
        os.dup2(origStdout, origStdoutFd)
        os.dup2(origStderr, origStderrFd)
        # clean up
        os.close(origStdout)
        os.close(origStderr)
        devnull.close()
