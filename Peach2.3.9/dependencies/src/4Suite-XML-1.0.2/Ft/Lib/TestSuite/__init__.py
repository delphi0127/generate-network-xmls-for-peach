########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Lib/TestSuite/__init__.py,v 1.3 2002/07/23 06:15:53 jkloth Exp $
"""
Package for testing utilities

Copyright 2002 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

__revision__ = "$Id: __init__.py,v 1.3 2002/07/23 06:15:53 jkloth Exp $"

def RemoveTests(list, ignored):
    for test in ignored:
        if test in list:
            list.remove(test)
    return list


def SortTests(list, atstart, atend=[]):
    ordered = {}
    position = 0
    for test in atstart:
        ordered[test] = position
        position += 1

    middle = position

    for test in atend:
        position += 1
        ordered[test] = position

    def dictsort(a, b, dict=ordered, default=middle):
        a = dict.get(a, default)
        b = dict.get(b, default)
        return cmp(a, b)

    list.sort(dictsort)

    return list


def Test(**attrs):
    import sys, os
    import TestSuite, Errors
    
    if not attrs.has_key('script_name'):
        attrs['script_name'] = sys.argv[0]

    if not attrs.has_key('script_args'):
        attrs['script_args'] = sys.argv[1:]

    # Create the TestSuite instance using the arguments to initialize it.
    test_dir = os.path.dirname(attrs['script_name']) or os.getcwd()
    try:
        sys.path.insert(0, test_dir)
        try:
            suite = TestSuite.TestSuite(attrs)
        except Errors.TestSuiteSetupError, msg:
            if attrs.has_key('name'):
                raise SystemExit, \
                      'error in %s test command: %s' % (attrs['name'], msg)
            else:
                raise SystemExit, \
                      'error in test command: %s' % msg

        try:
            ok = suite.parseCommandLine()
        except Errors.TestSuiteArgumentError, msg:
            raise SystemExit, \
                  suite.generateUsage() + '\nerror: %s' % msg

        if ok:
            try:
                suite.runTests()
            except (IOError, OSError), error:
                from distutils.util import grok_environment_error
                error = grok_environment_error(error)
                raise SystemExit(error)
            except Errors.TestSuiteError, error:
                raise SystemExit(str(error))
    finally:
        del sys.path[0]
    return suite
