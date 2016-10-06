########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Lib/TestSuite/TestCoverage.py,v 1.11 2006/08/11 15:50:12 jkloth Exp $
"""
A class that uses Python's profiler to help TestModule know which
functions have been called in a particular module.

Copyright 2004 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

import sys, os, inspect
from Ft.Lib import ImportUtil

class TestCoverage:

    def __init__(self, moduleName, ignored=None):
        self.module = moduleName
        self.path = ImportUtil.GetSearchPath(moduleName)
        self.ignored = ignored or []
        self.data = {}
        return

    def _getFunctionList(self):
        modules = []
        deferred = []
        for importer, name, ispkg in ImportUtil.IterModules(self.path):
            fullname = self.module + '.' + name
            try:
                __import__(fullname)
            except ImportError:
                deferred.append(fullname)
            else:
                modules.append(sys.modules[fullname])
        while deferred:
            changed = False
            for fullname in tuple(deferred):
                try:
                    __import__(fullname)
                except ImportError:
                    pass
                else:
                    changed = True
                    modules.append(sys.modules[fullname])
                    deferred.remove(fullname)
            if not changed:
                # no more modules able to be loaded
                raise ValueError(",".join([ item[1] for item in deferred ]))
                break

        data = {}
        for module in modules:
            for value in vars(module).values():
                if value in self.ignored: continue
                if inspect.isfunction(value):
                    data[value.func_code] = value
                elif inspect.isclass(value):
                    # Get the methods defined on this class
                    methods = inspect.getmembers(value, inspect.ismethod)
                    for name, method in methods:
                        if method in self.ignored or \
                           name in ('__str__', '__repr__', 'pprint'):
                            continue
                        # Make sure this method is not a C function
                        if inspect.isfunction(method.im_func):
                            data[method.im_func.func_code] = method

        # Only watch the objects that are defined directly in this package
        self.data = {}
        for code, object in data.items():
            if os.path.dirname(code.co_filename) in self.path:
                self.data[code] = object
        return

    def _dispatch(self, frame, event, arg):
        if event == 'call':
            fcode = frame.f_code
            # Any items remaining in self.data will be those not called
            if self.data.has_key(fcode):
                del self.data[fcode]
        return 1

    def _start(self, tester):
        self._getFunctionList()
        sys.setprofile(self._dispatch)
        return

    def _end(self, tester):
        # Stop watching function calls
        sys.setprofile(None)

        modules = {}
        for code, object in self.data.items():
            if inspect.ismethod(object):
                type = 'method'
                name = object.im_class.__name__ + '.' + object.__name__
                module = object.im_class.__module__
            else:
                type = 'function'
                name = object.__name__
                module = object.func_globals['__name__']
            if not modules.has_key(module):
                modules[module] = {'method' : [],
                                   'function' : [],
                                   }
            modules[module][type].append((name, code.co_firstlineno))

        tester.startGroup('Coverage Test')
        tester.startTest("Verifying called functions")

        keys = modules.keys()
        keys.sort()
        for module in keys:
            lines = []
            if modules[module]['function']:
                funcs = modules[module]['function']
                lines.append('Functions not called in %r:' % module)
                funcs.sort()
                for name, line in funcs:
                    lines.append('  %r on line %s' % (name, line))
            if modules[module]['method']:
                lines.append('Methods not called in %r:' % module)
                meths = modules[module]['method']
                meths.sort()
                for name, line in meths:
                    lines.append('  %r on line %s' % (name, line))
            tester.warning('\n'.join(lines))
        tester.testDone()
        tester.groupDone()
        return

