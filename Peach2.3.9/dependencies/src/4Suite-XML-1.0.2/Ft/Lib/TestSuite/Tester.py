########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Lib/TestSuite/Tester.py,v 1.13 2004/11/04 05:33:46 mbrown Exp $
"""
Provides the Tester class, which is the hub for all testing.

Copyright 2004 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

import sys, os, time
import traceback, linecache
from distutils import spawn
from sys import _getframe

from Ft.Lib import number, Terminal
from Ft.Lib.Terminal import AnsiEscapes

###########################################
#
#  Verbosity Levels
#  4  print out group headers, all test names and test results and debug messges
#  3  print out group headers, all test names and test results
#  2  print out group headers and errors and warnings
#  1  print out group headers and errors
#  0  Nothing
VERBOSE_DEBUG = 4
VERBOSE_MSG = 3
VERBOSE_WARN = 2
VERBOSE_ERROR = 1
VERBOSE_OFF = 0

SHOW_TESTS = VERBOSE_MSG
SHOW_GROUPS = VERBOSE_ERROR

_group_headers = ['#', '*', '=', ':', '%', '+', '-','@','$','&']


def _frame_lineno(frame):
    """
    Calculate correct line number of stack frame given in frame.
    """
    code = frame.f_code
    if not hasattr(code, 'co_lnotab'):
        return frame.f_lineno

    tab = code.co_lnotab
    line = code.co_firstlineno
    stopat = frame.f_lasti
    addr = 0
    for i in range(0, len(tab), 2):
        addr = addr + ord(tab[i])
        if addr > stopat:
            break
        line = line + ord(tab[i+1])
    return line


def extract_stack(frame=None, limit=None):
    if frame is None:
        # Skip this function body
        frame = _getframe(1)

    if limit is None:
        limit = getattr(sys, 'tracebacklimit', 1000)

    stack = []
    while frame and limit > 0:
        lineno = _frame_lineno(frame)
        co = frame.f_code
        filename = co.co_filename
        name = co.co_name
        line = linecache.getline(filename, lineno)
        if line:
            line = line.strip()
        else:
            line = None
        stack.append((filename, lineno, name, line))
        frame = frame.f_back
        limit -= 1
    stack.reverse()
    return stack

def format_stack(frame=None, limit=None):
    """Shorthand for 'format_list(extract_stack(f, limit))'."""
    return traceback.format_list(extract_stack(frame, limit))


class TestItem:
    def __init__(self, title):
        self.title = title
        self.messages = []
        self.hasErrors = 0
        self.hasWarnings = 0

        self.comparisons = 0
        self.compareTime = 0.0
        self.totalTime = 0.0
        self.runTime = 0.0
        self.startTime = time.time()
        return

    def __repr__(self):
        return '<%s, title=%r, compares=%d>' % (self.__class__.__name__,
                                                self.title,
                                                self.comparisons)

    def debug(self, msg):
        if msg:
            self.messages.append((VERBOSE_DEBUG, msg))
        return

    def message(self, msg):
        if msg:
            self.messages.append((VERBOSE_MSG, msg))
        return

    def warning(self, msg):
        self.hasWarnings = 1
        if msg:
            self.messages.append((VERBOSE_MSG, msg))
        return

    def error(self, msg):
        self.hasErrors = 1
        if msg:
            self.messages.append((VERBOSE_ERROR, msg))
        return

    def finish(self):
        self.totalTime = time.time() - self.startTime
        self.runTime = self.totalTime - self.compareTime
        return

class Tester:

    double_sep = '=' * 72
    single_sep = '-' * 72

    NORMAL = AnsiEscapes.Colors.DEFAULT
    GRAY = AnsiEscapes.Colors.FOREGROUND_GRAY
    RED = AnsiEscapes.Colors.FOREGROUND_RED
    GREEN = AnsiEscapes.Colors.FOREGROUND_LIME
    BROWN = AnsiEscapes.Colors.FOREGROUND_BROWN
    YELLOW = AnsiEscapes.Colors.FOREGROUND_YELLOW
    WHITE = AnsiEscapes.Colors.FOREGROUND_WHITE

    def __init__(self, stopOnError=1, useColor=1, verbose=VERBOSE_DEBUG,
                 stream=sys.stdout):
        self.stopOnError = stopOnError
        self.verbose = verbose
        self.stream = stream
        self.tty = Terminal.Terminal(stream, keepAnsiEscapes=useColor)
        self._writetty = self.tty.writetty

        self.test_data = {}
        self.groups = []
        self.test = None

        self.testTime = 0.0
        self._diffCommand = spawn.find_executable('diff')
        self._compareCtr = 0

        # Reporting information
        self.warnings = []
        self.failures = []
        self.exceptions = []
        self.totalGroups = 0
        self.totalTests = 0
        self.totalComparisons = 0
        return

    ### Testing Methods ###

    def startGroup(self, title):
        header = _group_headers[len(self.groups)]*10
        self.writeline(SHOW_GROUPS, '%s %s %s' % (header, title, header))

        self.groups.append(title)
        self.totalGroups += 1
        return

    def groupDone(self):
        if self.groups:
            del self.groups[-1]
        else:
            self.warning('groupDone called without active group')
        return

    def startTest(self, title):
        if self.test:
            # Add warning to current test
            self.warning('testDone not called')
            self.testDone()
            self.test = TestItem(title)
            # Add the warning to the new test as well
            self.warning('startTest called with active test')
        else:
            self.test = TestItem(title)
        self.totalTests += 1
        return

    def testDone(self):
        if not self.test:
            self.warning('testDone called without active test')
            return

        self.test.finish()

        if self.test.hasErrors:
            status = '[%sFAILED%s]' % (self.RED,
                                       self.NORMAL)
            level = VERBOSE_ERROR
        elif self.test.hasWarnings:
            status = '[%s WARN %s]' % (self.YELLOW,
                                       self.NORMAL)
            level = VERBOSE_WARN
        else:
            status = '[%s  OK  %s]' % (self.GREEN,
                                       self.NORMAL)
            level = SHOW_TESTS

        if not self.test.comparisons:
            title = '%s (%0.3f secs)' % (self.test.title,
                                         self.test.totalTime)
        else:
            title = '%s (%0.3f run, %0.3f total)' % (self.test.title,
                                                     self.test.runTime,
                                                     self.test.totalTime)
        spaces = self.tty.columns() - 9 # length of status
        if len(title) > spaces:
            self.writeline(level, title)
            self.writeline(level, ' '*spaces + status)
        else:
            self.writeline(level, title.ljust(spaces) + status)

        # Write the messages in the queue
        for level, line in self.test.messages:
            self.writeline(level, line)

        self.testTime += self.test.totalTime
        self.test = None
        return

    # -- result testing ----------------------------------------------

    def testException(self, func, args, etype, value={}, stackLevel=1, kwargs={}):
        # Increase stack trimming to include this function call
        stackLevel = stackLevel + 1
        try:
            func(*args, **kwargs)
        except etype, e:
            for attr, expected in value.items():
                if hasattr(e, attr):
                    self.compare(expected, getattr(e, attr),
                                 'exception attribute %s' % repr(attr),
                                 stackLevel=stackLevel)
        except:
            self.exception("Wrong exception raised")
        else:
            self.error("Expected exception '%s' not raised" % etype,
                       stackLevel=stackLevel)
        return

    def compare(self, expected, actual, msg=None, func=cmp, diff=0, stackLevel=1, funcArgs={}):
        """
        Uses func to compare the expected result with actual result
        of a regression test.

        diff is ignored.

        msg is an optional custom message to print if the
        comparison tests positive (i.e. the results differ).

        func is the comparison function to use, and must be a
        function that returns the same as the built-in cmp().

        stackLevel affects exception reporting.

        funcArgs is an optional dictionary of keyword arguments that
        will be passed to the comparison function, if the dictionary
        is not empty.
        """
        self.totalComparisons += 1

        # Normalize float values
        if type(expected) == type(actual) == float:
            if number.finite(expected):
                expected = float(str(expected))
            elif number.isnan(expected):
                expected = 'NaN'
            elif number.isinf(expected) > 0:
                expected = 'Inf'
            else:
                expected = '-Inf'

            if number.finite(actual):
                actual = float(str(actual))
            elif number.isnan(actual):
                actual = 'NaN'
            elif number.isinf(actual) > 0:
                actual = 'Inf'
            else:
                actual = '-Inf'

        # Make sure there was a message for this comparison
        if not msg:
            if self.test:
                self.test.comparisons += 1
                msg = 'Test %d' % (self.test.comparisons)
            else:
                msg = 'Test %d of all tests' % self.totalComparisons

        start = time.time()
        try:
            if funcArgs:
                res = func(expected, actual, **funcArgs)
            else:
                res = func(expected, actual)
            if res:
                # failure
                self.message(msg)
                if diff and self.verbose >= VERBOSE_DEBUG:
                    self._diff(expected, actual)

                error = '%sExpected:%s %s\n' % (self.GREEN,
                                                self.NORMAL,
                                                repr(expected))
                error += '%sCompared:%s %s' % (self.RED,
                                               self.NORMAL,
                                               repr(actual))
                self.error(error, stackLevel=(stackLevel+1))
                return 0
        finally:
            end = time.time()
            if self.test:
                self.test.compareTime += (end - start)

        # success
        return 1

    def compareIn(self, expected, actual, msg=None, stackLevel=1):
        """Test that 'actual' is in 'expected'"""
        func = lambda expected, actual: actual not in expected
        return self.compare(expected, actual, msg, func,
                            stackLevel=(stackLevel+1))

    # -- display functions -------------------------------------------

    def writeline(self, level, msg):
        if self.verbose >= level:
            self._writetty(msg)
            self._writetty('\n')
        return

    def debug(self, msg):
        """debug-level messages"""
        if self.test:
            self.test.debug(msg)
        else:
            self.writeline(VERBOSE_DEBUG, msg)
        return

    def message(self, msg):
        """informational"""
        if self.test:
            self.test.message(msg)
        else:
            self.writeline(VERBOSE_MSG, msg)
        return

    def warning(self, msg):
        """warning conditions"""
        titles = self.groups[:]
        if self.test:
            titles.append(self.test.title)
            self.test.warning(msg)
        else:
            self.writeline(VERBOSE_WARN, msg)
        self.warnings.append((titles, msg))
        return

    def error(self, msg, traceLimit=1, stackLevel=1):
        """error conditions"""
        if self.stopOnError:
            traceLimit = getattr(sys, 'tracebacklimit', 1000)

        # Trim off 'stackLevel' items from the frame stack.
        frame = _getframe(stackLevel)

        # Format only 'traceLimit' items in the stack
        lines = format_stack(frame, traceLimit)

        msg += '\n' + ''.join(lines)

        titles = self.groups[:]
        if self.test:
            titles.append(self.test.title)
            self.test.error(msg)
        else:
            self.writeline(VERBOSE_ERROR, msg)
        self.failures.append((titles, msg))

        if self.stopOnError:
            self.testDone()
            raise SystemExit(1)
        return

    def exception(self, msg):
        """system is unusable""" # ??? looks like it's being used anyway
        if not sys.exc_info()[2]:
            raise AttributeError('No exception; use error method instead')

        try:
            etype, value, tb = sys.exc_info()
            lines = traceback.format_exception(etype, value, tb)
        finally:
            etype = value = tb = None

        msg += '\n' + ''.join(lines)

        titles = self.groups[:]
        if self.test:
            titles.append(self.test.title)
            self.test.error(msg)
        else:
            self.writeline(VERBOSE_ERROR, msg)
        self.exceptions.append((titles, msg))

        if self.stopOnError:
            self.testDone()
            raise SystemExit(1)
        return

    def _displayList(self, title, color, list):
        for titles, message in list:
            header = ': '.join(titles)
            self._writetty('\n%s%s: %s%s\n' % (color, title, header,
                                               self.NORMAL))
            self._writetty(message)
            self._writetty('\n')
        if list:
            self._writetty('\n%s\n' % self.single_sep)
        return

    def report(self):
        self._writetty('\n')
        self._writetty(self.double_sep)
        self._writetty('\n')

        self._displayList('WARN', self.YELLOW, self.warnings)
        self._displayList('FAIL', self.RED, self.failures)
        self._displayList('EXCEPTION', self.WHITE, self.exceptions)

        self._writetty('\n')
        self._writetty("  Test Groups Run: %d\n" % self.totalGroups)
        self._writetty("   Test Items Run: %d\n" % self.totalTests)
        self._writetty(" Results Compared: %d\n" % self.totalComparisons)
        self._writetty("Total Time To Run: %0.3fs\n" % self.testTime)
        self._writetty('\n')

    # -- internal functions ------------------------------------------

    def _diff(self, expected, compared):
        # get the temporary file directory
        import tempfile
        tempdir = tempfile.gettempdir()

        if self._diffCommand:
            # create the expected output file
            expected_file = os.path.join(tempdir, 'expected')
            fd = open(expected_file, 'w')
            fd.write(str(expected))
            fd.close()

            # create the compared output file
            compared_file = os.path.join(tempdir, 'compared')
            fd = open(compared_file, 'w')
            fd.write(str(compared))
            fd.close()

            # run diff, capturing stdout and stderr
            cmdline = '%s -u %s %s' % (self._diffCommand, expected_file,
                                       compared_file)
            self.debug(cmdline)
            f_in, f_out = os.popen4(cmdline)
            f_in.close()
            self.debug(f_out.read())
            f_out.close()

            os.unlink(expected_file)
            os.unlink(compared_file)
        return
