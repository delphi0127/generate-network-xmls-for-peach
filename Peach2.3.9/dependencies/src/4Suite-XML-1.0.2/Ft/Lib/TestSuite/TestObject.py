########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Lib/TestSuite/TestObject.py,v 1.2 2002/08/16 17:38:09 molson Exp $
"""
Provides the TestObject base class used in TestSuite modules.

Copyright 2002 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

__revision__ = "$Id: TestObject.py,v 1.2 2002/08/16 17:38:09 molson Exp $"

import os
import TestMode

class TestObject:
    """Base class for all test objects."""

    modes = None
    tests = None

    def __init__(self, name):
        self.name = name
        return

    def __str__(self):
        return "<%s, name %r>" % (self.__class__.__name__, self.name)

    def run(self, tester):
        raise NotImplementedError

    def getModes(self):
        return self.modes

    def getTests(self):
        return self.tests

    def showTests(self, indent):
        return
