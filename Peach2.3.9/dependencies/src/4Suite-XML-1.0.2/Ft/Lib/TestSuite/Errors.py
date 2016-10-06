########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Lib/TestSuite/Errors.py,v 1.1 2002/07/17 22:57:31 jkloth Exp $
"""
Exceptions used in TestSuite modules.

Copyright 2002 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

__revision__ = '$Id: Errors.py,v 1.1 2002/07/17 22:57:31 jkloth Exp $'

class TestSuiteError(Exception): pass

class TestSuiteSetupError(TestSuiteError): pass

class TestSuiteInternalError(TestSuiteError): pass

class TestSuiteArgumentError(TestSuiteError): pass

