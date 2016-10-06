########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Lib/TestSuite/TestSuite.py,v 1.13 2006/08/11 15:50:12 jkloth Exp $
"""
Provides the TestSuite class, which represents the package(s) to test.

Copyright 2006 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

__revision__ = "$Id: TestSuite.py,v 1.13 2006/08/11 15:50:12 jkloth Exp $"

import getopt, sys, os, inspect
from types import *

import TestLoader, TestModule, Tester
from Errors import *

USAGE = """\
Usage:
  %(script)s [options] [test] [...]
  %(script)s --help-tests
  %(script)s --help
  %(script)s --help [test]

Examples:
  %(script)s                        run default set of tests
  %(script)s directory              run all tests in 'directory'
  %(script)s directory%(sep)sfile         run just 'file' from 'directory'
"""

class TestSuite:
    """
    A command-line program that runs a set of tests; this is primarily
    for making test modules conveniently executable.
    """

    options = [
        ('help', 'h', 'Show detailed help message'),
        ('help-tests', 't', 'List all available tests'),
        ('verbose', 'v', 'Increase display verbosity'),
        ('quiet', 'q', 'Decrease display verbosity'),
        ('mode=', 'm', 'Add mode to default modes to run'),
        ('skip=', 'k', 'Remove a mode from the modes to run'),
        ('full', 'f', 'Use all modes'),
        ('stop', 's', 'Stop on errors'),
        ('nocolor', 'n', 'Disable ANSI color sequences'),
        ('noreport', 'r', 'Disable report generation'),
        ('outfile=', 'o', 'Specify an output file for all results'),
        ('offline', 'l', 'Skip tests requiring internet connection')
        ]

    negative_opts = {'quiet' : 'verbose',
                     'nocolor' : 'color',
                     'noreport' : 'report',
                     }

    # options that can only be true or false
    boolean_opts = ('full', 'stop', 'nocolor', 'noreport', 'offline',
                    'help', 'help-tests')

    def __init__(self, attrs):

        # Default values for command-line options
        self.verbose = 2    # counter
        self.mode = []      # string list
        self.skip = []      # string list
        self.full = 0       # boolean
        self.stop = 0       # boolean
        self.color = 1      # boolean
        self.report = 1     # boolean
        self.outfile = ''   # string
        self.offline = 0    # boolean
        self.help = 0       # boolean
        self.help_tests = 0 # boolean

        # 'script_name' and 'script_args' are usually set to sys.argv[0]
        # and sys.argv[1:], but they can be overridden when the caller is
        # not necessarily a setup script run from the command-line.
        self.script_name = None
        self.script_args = None
        self.name = None
        self.packages = None

        # Now we'll use the attrs dictionary (ultimately, keyword args from
        # the setup script) to possibly override any or all of these
        # distribution options.
        for key, value in attrs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise TestSuiteSetupError('invalid test option %r' % key)
        return

    def _grokOptions(self):
        long_opts = []
        short_opts = []
        short2long = {}

        for option in self.options:
            try:
                (long, short, help) = option
            except ValueError:
                raise TestSuiteInternalError, \
                          'invalid option tuple %r' % option

            # Type and value check the option names
            if not isinstance(long, StringType) or len(long) < 2:
                raise TestSuiteInternalError, \
                          'invalid long option %r' % long

            if short and not isinstance(short, StringType) and len(short) > 1:
                raise TestSuiteInternalError, \
                          'invalid short option %r' % short


            long_opts.append(long)

            if short:
                if long.endswith('='):
                    short = short + ':'
                    long = long[:-1]

                short2long[short[0]] = long
                short_opts.append(short)

        return (''.join(short_opts), long_opts, short2long)

    def _getopt(self, args):
        short_opts, long_opts, short2long = self._grokOptions()

        parsed_args = []
        parsed_opts = []

        while args:
            try:
                opts, args = getopt.getopt(args, short_opts, long_opts)
            except getopt.error, error:
                raise TestSuiteArgumentError(str(error))

            # Convert all options to their long form
            for opt, value in opts:
                if len(opt) == 2 and opt[0] == '-':
                    # a short option
                    opt = short2long[opt[1]]
                else:
                    # a long option
                    opt = opt[2:]
                parsed_opts.append((opt, value))

            # Scan the arguments for any remaining options

            while args and args[0][:1] != '-':
                arg = args.pop(0)
                # If the arg is an existing file/directory, convert it to a
                # Python package path, otherwise assume a valid package.
                pathname = os.path.normpath(arg)
                if os.path.isdir(pathname):
                    # check for package directory
                    source = pathname + os.sep + '__init__.py'
                    compiled = source + (__debug__ and 'c' or 'o')
                    if os.path.exists(source) or os.path.exists(compiled):
                        arg = pathname.replace(os.sep, '.')
                elif os.path.exists(pathname):
                    # Convert path to pkg.mod notation
                    modulename = inspect.getmodulename(pathname)
                    if modulename is not None:
                        names = pathname.split(os.sep)
                        names[-1] = modulename
                        arg = '.'.join(names)

                # Add Python package path to the parsed arguments
                parsed_args.append(arg)

        # Handle the options now
        for (name, value) in parsed_opts:
            if name in self.boolean_opts:
                # If specified it must be true
                value = 1

            alias = self.negative_opts.get(name)
            if alias:
                attr = alias.replace('-', '_')
            else:
                attr = name.replace('-', '_')

            if not hasattr(self, attr):
                raise TestSuiteInternalError, \
                      "missing attribute for option %r" % name

            current = getattr(self, attr)
            if name in self.boolean_opts:
                # boolean
                if alias:
                    setattr(self, attr, 0)
                else:
                    setattr(self, attr, 1)
            elif isinstance(current, IntType):
                # counter
                if alias:
                    setattr(self, attr, current - 1)
                else:
                    setattr(self, attr, current + 1)
            elif isinstance(current, ListType):
                # string list
                if alias:
                    while value in current:
                        current.remove(value)
                else:
                    current.append(value)
            elif isinstance(current, StringType):
                # string
                setattr(self, attr, value)
            else:
                raise TestSuiteInternalError, \
                          "unknown type for option %r" % name

        return parsed_args

    def addTests(self, packages):
        for package in packages:
            testobj = self.test
            for step in package.split('.'):
                # See if this step has already been added
                for test in testobj.tests:
                    if test.name == step:
                        # Found an existing test, reuse it
                        testobj = test
                        break
                else:
                    # Create a new test
                    testobj = testobj.addTest(step)
        return

    def parseCommandLine(self):
        """
        Parse the test script's command line, taken from the 'script_args'
        instance attribute (which defaults to 'sys.argv[1:]').  This is
        first processed for options that set attributes of the TestSuite
        instance.  Then, it is scanned for test arguments.
        """
        packages = self._getopt(self.script_args)

        self.test = TestLoader.TestLoader(self.name, '', self.mode,
                                          self.skip, self.full)
        if self.help_tests:
            # ignore any supplied arguments
            print self.generateUsage()
            print 'Available tests:'
            self.showTests()
            return 0 # done

        if self.help:
            # display usage and if there are tests specified info about them
            self.showHelp(packages)
            return 0 # done

        self.addTests(packages or self.packages)

        # Signal caller that is OK to continue
        return 1

    def showTests(self):
        indent = ' '*2
        self.addTests(self.packages)
        for test in self.test.getTests():
            test.showTests(indent)
        return

    def generateUsage(self):
        usage = USAGE % {'script' : os.path.basename(self.script_name),
                         'sep' : os.sep}
        return usage

    def showHelp(self, tests):
        print self.generateUsage()

        # Display the options
        print 'Options:'
        display_opts = []
        max_opt = 0
        for opt in self.options:
            long = opt[0]
            if long[-1] == '=':
                long = '%s<%s>' % (long, long[:-1])
            display = '-%s, --%s' % (opt[1], long)
            display_opts.append((display, opt[2]))
            if len(display) > max_opt:
                max_opt = len(display)
        for display, help in display_opts:
            print '  %-*s  %s' % (max_opt, display, help)
        print

        # Display detailed help for the given tests
        for path in tests:
            modes = []

            testobj = self.test
            for step in path.split('.'):
                testobj = testobj.loadTest(step)
                for mode in testobj.getModes([], [], 1):
                    if mode.name:
                        modes.append((mode.name, testobj.path))

            if modes:
                print 'Modes for %r:' % testobj.path
                for (name, path) in modes:
                    if path != testobj.path:
                        print "  %s (declared in %s)" % (name, path)
                    else:
                        print "  %s" % name
                print

            subtests = [ test for test in testobj.getTests()
                         if isinstance(test, TestModule.TestModule) ]
            if subtests:
                print 'Sub-tests for %r:' % testobj.path
                for test in subtests:
                    print "  %s" % test.name
                print
        return

    def runTests(self):
        tester = Tester.Tester(self.stop, self.color, self.verbose)
        tester.offline = self.offline
        try:
            for test in self.test.getTests():
                test.run(tester)
        except KeyboardInterrupt:
            sys.stderr.write('\n%s\n' % ('='*72))
            sys.stderr.write('\nTesting interrupted\n')

        if self.report:
            tester.report()
        return

