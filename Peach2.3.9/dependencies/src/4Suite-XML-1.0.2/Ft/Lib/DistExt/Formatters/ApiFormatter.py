import os, re, pydoc, inspect, types, imp, stat, time
import XmlFormatter

# Get the list of types to not document
_builtin_types = vars(types).values()
_builtin_types = [ t for t in _builtin_types if type(t) is types.TypeType ]

# The list of modules which have objects in the global namespace
_global_module_names = ('__builtin__', 'exceptions')

# Regex for extracting the argument list from a builtin function's docstring
# WARNING - tuple arguments in the arglist will break this
_re_arglist = re.compile(' *[a-zA-Z_][a-zA-Z0-9_]* *\((?P<arglist>[^)]*) *\)')

# Some names are invisible; these are not documented at all.
try:
    _visiblename = pydoc.visiblename
except AttributeError:
    _special_names = ['builtins', 'doc', 'file', 'path', 'module', 'name']
    _special_names = [ '__%s__' % name for name in _special_names ]
    def _visiblename(name):
        """Decide whether to show documentation on a variable."""
        # Certain special names are redundant.
        if name in _special_names: return 0
        # Private names are hidden, but special names are displayed.
        if name.startswith('__') and name.endswith('__'): return 1
        return not name.startswith('_')

class ApiFormatter(XmlFormatter.XmlFormatter):

    document_type = types.ModuleType

    def __init__(self, command, modules):
        XmlFormatter.XmlFormatter.__init__(self, command)
        self.module_info = modules
        return

    # Some names are not invisible, but are still not public.  Such names
    # which are not public are still documented, but this documentation is
    # not displayed, because these "private" names should not be used
    # outside the given module.
    def ispublic(self, name):
        if hasattr(self.module, '__all__'):
            return (name in self.module.__all__) and 'yes' or 'no'
        else:
            return (not name.startswith('_')) and 'yes' or 'no'

    def isdocumented(self, name):
        return name in self.module_info and 'yes' or 'no'

    def document(self, module):
        """
        Produce documentation for a given module object.
        """
        module_name = module.__name__
        attributes = {'name' : module_name}
        self.start_element('module', attributes)

        absfile, module_type = self.module_info[module_name]
        mtime = os.stat(absfile)[stat.ST_MTIME]
        mtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mtime))
        self.write_element('modification-date', content=mtime)

        self.write_description(module)

        # standard module metadata
        for attr in ['author', 'credits', 'date', 'version']:
            if hasattr(module, '__%s__' % attr):
                content = self.escape(str(getattr(module, '__%s__' % attr)))
                self.write_element(attr, content=content)

        submodules = []
        if module_type == imp.PKG_DIRECTORY:
            name = re.escape(module_name)
            submodule_match = re.compile(r'^%s\.([^.]+)$' % name).match
            for fullname in self.module_info:
                match = submodule_match(fullname)
                if match:
                    name = match.group(1)
                    try:
                        submod = pydoc.safeimport(fullname)
                    except:
                        submod = None
                    if submod is None:
                        # Could not import for some reason, create a stub
                        submod = imp.new_module(fullname)
                    submodules.append((name, submod))

        all = getattr(module, '__all__', [])

        # Only document the modules listed in __all__.
        for name, member in inspect.getmembers(module, inspect.ismodule):
            if name in all:
                submodules.append((name, member))
        if submodules:
            submodules.sort()
            self.section('modules', submodules, self.doc_submodule)

        # Only document the classes defined in this module or
        # are listed in __all__.
        def isclass(object):
            """
            Replacement for inspect's broken isclass() which fails for
            instances of classes which define a custom __getattr__.
            """
            return isinstance(object, (types.ClassType, type))

        classes = [ t for t in inspect.getmembers(module, isclass)
                    if ((inspect.getmodule(t[1]) or module) is module or
                        t[0] in all) ]
        if classes:
            self.section('classes', classes, self.doc_class)

        # Only document the functions defined in this module or
        # are listed in __all__.
        funcs = [ t for t in inspect.getmembers(module, inspect.isroutine)
                  if ((inspect.getmodule(t[1]) or module) is module or
                      t[0] in all) ]
        if funcs:
            self.section('functions', funcs, self.doc_function)

        # Only document the "visible" objects or those listed in __all__.
        globals = [ t for t in inspect.getmembers(module, pydoc.isdata)
                    if t[0] in all or _visiblename(t[0]) ]
        if globals:
            self.section('globals', globals, self.doc_global)

        self.end_element('module')
        return

    def doc_submodule(self, module, name):
        """Produce XML documentation for a submodule"""
        realname = module.__name__
        name = name or realname

        attributes = {'name' : name,
                      'realname' : realname,
                      'public' : name.startswith('_') and 'no' or 'yes',
                      'documented' : self.isdocumented(realname),
                      }

        self.start_element('module-reference', attributes)

        self.write_description(module)

        self.end_element('module-reference')
        return

    def doc_class(self, klass, name):
        """Produce XML documentation for a given class object."""
        realname = klass.__name__
        name = name or realname

        attributes = {'name' : name,
                      'public' : self.ispublic(name),
                      }
        if name != realname:
            attributes['realname'] = realname

        self.start_element('class', attributes)

        if klass.__bases__:
            self.start_element('bases')
            for base in klass.__bases__:
                attributes = {
                    'class' : base.__name__,
                    'documented' : self.isdocumented(base.__module__),
                    }
                if base.__module__ not in _global_module_names:
                    attributes['module'] = base.__module__
                self.write_element('base', attributes)
            self.end_element('bases')

        self.write_description(klass)

        self.start_element('method-resolution-order')
        mro = list(inspect.getmro(klass))
        bases = {}
        for base in mro:
            attributes = {'name' : base.__name__,
                          }
            if base.__module__ not in _global_module_names:
                attributes['module'] = base.__module__
            self.write_element('base', attributes)
        self.end_element('method-resolution-order')

        attrs = inspect.classify_class_attrs(klass)
        attrs = [ t for t in attrs if _visiblename(t[0]) ]
        while attrs:
            if mro:
                thisclass = mro.pop(0)
            else:
                thisclass = attrs[0][2]

            inherited_attrs = [ t for t in attrs if t[2] is not thisclass ]
            attrs = [ t for t in attrs if t[2] is thisclass ]

            # Sort attrs by name (which is the first item in the tuple)
            attrs.sort()

            # Group the attributes into 'methods' and 'members', where:
            #  methods = the method types and functions from 'data'
            #  members = properties and the non-functions from 'data'
            methods = []
            members = []
            for name, kind, homecls, obj in attrs:
                # Fixup results from classify_class_attrs()
                if kind == 'method':
                    # inspect.classify_class_attrs gets the methods
                    # from the class __dict__ which returns functions,
                    # not methods
                    obj = getattr(klass, name)
                elif inspect.isbuiltin(obj):
                    # built-in method (C functions bound to class)
                    kind = 'method'

                info = (obj, name, homecls, kind)
                if kind.endswith('method'):
                    methods.append(info)
                else:
                    members.append(info)

            inherited = thisclass is not klass
            if inherited:
                attributes = {
                    'class' : thisclass.__name__,
                    'documented' : self.isdocumented(thisclass.__module__),
                    }
                if thisclass.__module__ not in _global_module_names:
                    attributes['module'] = thisclass.__module__

                if methods:
                    self.start_element('inherited-methods', attributes)
                    for info in methods:
                        self.doc_inherited(*info)
                    self.end_element('inherited-methods')

                if members:
                    self.start_element('inherited-members', attributes)
                    for info in members:
                        self.doc_inherited(*info)
                    self.end_element('inherited-members')
            else:
                if methods:
                    self.start_element('methods', attributes)
                    for info in methods:
                        if inspect.ismethoddescriptor(info[0]):
                            self.doc_methoddescriptor(*info)
                        else:
                            self.doc_method(*info)
                    self.end_element('methods')

                if members:
                    self.start_element('members', attributes)
                    for info in members:
                        self.doc_member(*info)
                    self.end_element('members')

            attrs = inherited_attrs

        self.end_element('class')
        return

    def format_arg(self, arg, default=None):
        attributes = {}
        if default is not None:
            attributes['default'] = default
        if type(arg) in [types.TupleType, types.ListType]:
            self.start_element('sequence', attributes)
            for a in arg:
                self.format_arg(a)
            self.end_element('sequence')
        else:
            attributes['name'] = arg
            self.write_element('arg', attributes)
        return

    def doc_arguments(self, object):
        self.start_element('arguments')

        if inspect.isfunction(object):
            args, varargs, varkw, defaults = inspect.getargspec(object)

            if defaults:
                firstdefault = len(args) - len(defaults)

            for i in xrange(len(args)):
                if defaults and i >= firstdefault:
                    default = repr(defaults[i - firstdefault])
                else:
                    default = None
                self.format_arg(args[i], default)

            if varargs:
                self.write_element('var-args', {'name' : varargs})

            if varkw:
                self.write_element('var-keywords', {'name' : varkw})
        else:
            arglist = '...'
            if inspect.isbuiltin(object):
                # Extract argument list from docstring
                match = _re_arglist.match(pydoc.getdoc(object))
                if match:
                    arglist = match.group('arglist')
            self.write_element('unknown', content=arglist)

        self.end_element('arguments')
        return

    def doc_method(self, method, name, klass, kind):
        """
        Document a method, class method or static method as given by 'kind'
        """
        attributes = {'name' : name,
                      'id' : klass.__name__ + '-' + name,
                      'public' : self.ispublic(name),
                      }
        realname = method.__name__
        if name != realname:
            attributes['realname'] = realname
            # aliased methods fail the 'is' test but compare true
            if getattr(klass, realname, None) == method:
                attributes['realid'] = klass.__name__ + '-' + realname

        tagname = kind.replace(' ', '-')
        self.start_element(tagname, attributes)

        self.write_description(method)

        func = getattr(method, 'im_func', method)
        self.doc_arguments(func)

        # This always returns the passed in class as the first item
        for base in inspect.getmro(klass)[1:]:
            overridden = getattr(base, name, None)
            if overridden:
                attributes = {
                    'class' : base.__name__,
                    'documented' : self.isdocumented(base.__module__),
                    }
                if base.__module__ not in _global_module_names:
                    attributes['module'] = base.__module__
                self.write_element('overrides', attributes)
                break

        self.end_element(tagname)
        return

    def doc_methoddescriptor(self, descr, name, klass, kind):
        """
        Document a class method or static method as given by 'kind'
        """
        attributes = {'name' : name,
                      'id' : klass.__name__ + '-' + name,
                      'public' : self.ispublic(name),
                      }
        tagname = kind.replace(' ', '-')
        self.start_element(tagname, attributes)

        self.write_description(descr)
        self.doc_arguments(descr)

        self.end_element(tagname)
        return

    def doc_member(self, object, name, klass, kind):
        """Produce XML documentation for a data object."""
        attributes = {'name' : name,
                      'id' : klass.__name__ + '-' + name,
                      'public' : self.ispublic(name),
                      }
        self.start_element('member', attributes)

        # SWIG wrapped objects throw exceptions with getattr(obj, attr, None)
        # but not with hasattr(obj, attr)
        if ((callable(object) or kind == 'property') and
            hasattr(object, '__doc__') and getattr(object, '__doc__')
            ):
            self.write_description(object)

        self.write_element('value', content=self.repr(object))

        self.end_element('member')
        return

    def doc_inherited(self, object, name, klass, kind):
        """Produce XML documentation for an inherited object."""
        attributes = {'name' : name,
                      'public' : self.ispublic(name),
                      }
        self.write_element('member-reference', attributes)
        return

    def doc_function(self, func, name):
        """
        Document a function
        """
        realname = func.__name__
        if realname == '<lambda>':
            realname = 'lambda'
        name = name or realname

        attributes = {'name' : name,
                      'id' : name,
                      'public' : self.ispublic(name),
                      }
        if name != realname:
            attributes['realname'] = realname

        self.start_element('function', attributes)

        self.write_description(func)

        self.doc_arguments(func)

        self.end_element('function')
        return

    def doc_global(self, object, name):
        """Produce XML documentation for a data object."""
        attributes = {'name' : name,
                      'id' : name,
                      'public' : self.ispublic(name),
                      }

        self.start_element('global', attributes)

        # Add descriptions for globals that:
        # - are instances and have a different docstring than their class, or
        # - are not a builtin type and have a non-empty docstring
        #
        # SWIG wrapped objects throw exceptions with getattr(obj, attr, None)
        # but not with hasattr(obj, attr)
        if ((isinstance(object, types.InstanceType) and
             object.__doc__ != object.__class__.__doc__) or
            (type(object) not in _builtin_types and
             hasattr(object, '__doc__') and getattr(object, '__doc__'))
            ):
            self.write_description(object)

        self.write_element('value', content=self.repr(object))

        self.end_element('global')
        return

    def write_description(self, object):
        """Produce XML tag(s) for an object description."""
        docstring = self.escape(pydoc.getdoc(object))

        paragraphs = docstring.split('\n\n')
        if paragraphs:
            abstract = paragraphs[0]
            description = '\n\n'.join(paragraphs[1:])
        else:
            abstract = None
            description = None

        self.write_element('abstract', content=abstract)
        self.write_element('description', content=description)
        return

# function not available in Python 2.1
if not hasattr(inspect, 'getmro'):
    def _searchbases(cls, accum):
        # Simulate the "classic class" search order.
        if cls in accum:
            return
        accum.append(cls)
        for base in cls.__bases__:
            _searchbases(base, accum)

    def getmro(cls):
        "Return list of base classes (including cls) in method resolution order."
        result = []
        _searchbases(cls, result)
        return result
    inspect.getmro = getmro

# function not available in Python 2.1
if not hasattr(inspect, 'classify_class_attrs'):
    def classify_class_attrs(cls):
        """Return list of attribute-descriptor tuples.

        For each name defined on class, cls, the return list contains a
        4-tuple with these elements:

            0. The name (a string).

            1. The kind of attribute this is, one of these strings:
                   'method'   any flavor of method
                   'data'     not a method

            2. The class which defined this attribute (a class).

            3. The object as obtained directly from the defining class's
               __dict__, not via getattr.
        """

        # This mimics a Python 2.2 dir(), which returns an alphabetized list
        # of all reachable attribute names.
        bases = getmro(cls)
        bases.reverse()
        combined = {}
        for baseclass in bases:
            for name, value in baseclass.__dict__.items():
                combined[name] = (baseclass, value)
        names = combined.keys()
        names.sort()

        result = []
        for name in names:
            true_class, obj = combined[name]
            # Classify the object.
            if inspect.ismethod(getattr(cls, name)):
                kind = "method"
            else:
                kind = "data"
            result.append((name, kind, true_class, obj))
        return result
    inspect.classify_class_attrs = classify_class_attrs
