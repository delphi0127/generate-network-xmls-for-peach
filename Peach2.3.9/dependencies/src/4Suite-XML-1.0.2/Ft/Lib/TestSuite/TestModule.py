########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Lib/TestSuite/TestModule.py,v 1.9 2006/08/11 15:50:12 jkloth Exp $
"""
Provides the TestModule class for wrapping modules/packages.

Copyright 2006 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

import os
from Ft.Lib import ImportUtil
import TestLoader, TestFunction, TestMode, TestCoverage

class TestModule(TestLoader.TestLoader):
    """Test object for a module or package."""

    def __init__(self, name, module, addModes, skipModes, allModes):
        TestLoader.TestLoader.__init__(self, name, module.__name__, addModes,
                                       skipModes, allModes)
        self.module = module
        self.modes = self.getModes(addModes, skipModes, allModes)
        loader = ImportUtil.FindLoader(self.path)
        self.isPackage = loader.is_package(self.path)
        return

    def getModes(self, addModes, skipModes, allModes):
        # Create the list of modes we will run
        modes = getattr(self.module, 'MODES', [TestMode.DefaultMode()])
        run_modes = []
        if allModes:
            # Use whatever modes are not skipped
            for mode in modes:
                if mode.name not in skipModes:
                    run_modes.append(mode)
        else:
            # Use the specified modes that are not also skipped
            for mode in modes:
                if mode.name in addModes and mode.name not in skipModes:
                    run_modes.append(mode)

            # If no specified modes found, use the default
            if not run_modes:
                for mode in modes:
                    if mode.default and mode.name not in skipModes:
                        run_modes.append(mode)
        return run_modes

    def getTests(self):
        """
        Get the test objects contained within this module.
        """

        # If there are no cached results, gather the sub-tests based on
        # the type of module.
        if not self.tests:

            # Get the test function(s) defined in this module
            for name in dir(self.module):
                if name == 'Test': #name.startswith('Test'):
                    obj = getattr(self.module, name)
                    if callable(obj):
                        self.tests.append(TestFunction.TestFunction(obj))

            # If this is a package, get the available modules
            if self.isPackage:
                files = []
                dirs = []
                path = ImportUtil.GetSearchPath(self.path)
                for importer, name, ispkg in ImportUtil.IterModules(path):
                    if ispkg:
                        dirs.append(name)
                    else:
                        files.append(name)

                # Default running order is alphabetical
                dirs.sort()
                files.sort()

                # Let the module manipulate the test lists
                if hasattr(self.module, 'PreprocessFiles'):
                    (dirs, files) = self.module.PreprocessFiles(dirs, files)

                # Add the test lists to our available tests
                for name in dirs + files:
                    self.addTest(name)

                # If this modules defines a CoverageModule, add the coverage
                # start and end functions.
                if hasattr(self.module, 'CoverageModule'):
                    ignored = None
                    if hasattr(self.module,'CoverageIgnored'):
                        ignored = self.module.CoverageIgnored
                    ct = TestCoverage.TestCoverage(self.module.CoverageModule,ignored)
                    self.tests.insert(0, TestFunction.TestFunction(ct._start))
                    self.tests.append(TestFunction.TestFunction(ct._end))

        return self.tests

    def showTests(self, indent):
        if self.isPackage:
            # A package
            print '%s%s%s' % (indent, self.name, os.sep)
            new_indent = indent + ' '*2
            for test in self.getTests():
                test.showTests(new_indent)
        else:
            # A simple module
            print '%s%s' % (indent, self.name)
        return

    def run(self, tester):
        # Determine the modes
        tester.startGroup(self.name)

        modes = []
        for mode in self.modes:
            if mode.initialize(tester):
                modes.append(mode)

        if not modes:
            tester.warning("All modes have been skipped")

        for mode in modes:
            mode.start(tester)
            try:
                have_run = 0
                for test in self.getTests():
                    self.runTest(tester, test)
                    have_run = 1
                if not have_run:
                    tester.warning('Module does define any tests')
            finally:
                mode.finish(tester)

        tester.groupDone()
        return

    def runTest(self, tester, testObject):
        # Saved to check for misbehaving tests
        depth = len(tester.groups)

        # Run the test
        try:
            testObject.run(tester)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            tester.exception('Unhandled exception in test')
            # Clean up for the interrupted test
            if tester.test:
                tester.testDone()
            while len(tester.groups) > depth:
                tester.groupDone()
            return

        if tester.test:
            tester.warning('Failed to finish test (fixed)')
            tester.testDone()

        # Verify proper group count
        count = len(tester.groups) - depth
        if count < 0:
            tester.error('Closed too many groups')
        elif count > 0:
            tester.warning('Failed to close %d groups (fixed)' % count)
            while count:
                count -= 1
                tester.message('Closing group %s' % tester.groups[-1])
                tester.groupDone()
        return
