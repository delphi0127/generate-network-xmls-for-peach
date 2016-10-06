########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Lib/TestSuite/TestMode.py,v 1.2 2002/07/18 18:15:58 molson Exp $
"""
Provides the TestMode base class for testing modes.

Copyright 2002 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

__revision__ = "$Id: TestMode.py,v 1.2 2002/07/18 18:15:58 molson Exp $"

class TestMode:
    def __init__(self, name, default):
        self.name = name
        self.default = default
        self.initialized = None
        return
    
    def initialize(self, tester):
        """
        Called the first time this mode is used. A return value of false
        signals that this mode is not to be used.
        """
        if self.initialized is None:
            # First time through
            self.initialized = self._init(tester)
        return self.initialized

    def start(self, tester):
        """
        Called before beginning any tests.
        """
        tester.startGroup(self.name)
        self._pre(tester)
        return

    def finish(self, tester):
        """
        Called when all tests have run to completion (or exception).
        """
        self._post(tester)
        tester.groupDone()
        return

    # -- hooks for subclasses ----------------------------------------

    def _init(self, tester):
        return 1

    def _pre(self, tester):
        pass

    def _post(self, tester):
        pass

class DefaultMode(TestMode):
    def __init__(self):
        TestMode.__init__(self, '', 1)
        return
    def initialize(self, tester):
        return 1
    def start(self, tester):
        return
    def finish(self, tester):
        return

