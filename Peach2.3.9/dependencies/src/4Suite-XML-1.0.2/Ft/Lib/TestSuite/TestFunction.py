########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Lib/TestSuite/TestFunction.py,v 1.1 2002/07/17 22:57:31 jkloth Exp $
"""
Provides the TestFunction class for wrapping functions.

Copyright 2002 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

__revision__ = "$Id: TestFunction.py,v 1.1 2002/07/17 22:57:31 jkloth Exp $"

import TestObject

class TestFunction(TestObject.TestObject):
    """A test object that wraps a testing function."""
    def __init__(self, function):
        TestObject.TestObject.__init__(self, function.__name__)
        # Use the function as the run() method
        self.run = function
        return
