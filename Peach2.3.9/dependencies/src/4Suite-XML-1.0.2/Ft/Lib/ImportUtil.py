########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Lib/ImportUtil.py,v 1.1.2.2 2006/12/08 22:50:53 jkloth Exp $
"""
Utilites for working with Python PEP 302 import hooks.

Copyright 2006 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

from __future__ import generators
import os
import sys
import imp
import time
import types
import cStringIO
try:
    from zipimport import zipimporter
except ImportError:
    # placeholder for Python 2.2 to simplify code paths
    class zipimporter(object): pass

__all__ = [
    # Module Utilities
    'FindLoader', 'FindImporter', 'GetImporter', 'IterModules',
    'GetLastModified', 'GetSearchPath',
    # Resource Utilities
    'OsPathToResource', 'NormalizeResource', 'GetResourceFilename',
    'GetResourceString', 'GetResourceStream', 'GetResourceLastModified',
    ]

# Indicate that the use of "special" names is handled in a "zip-safe" way.
__zipsafe__ = True

IMP_SEARCH_ORDER = [ desc[0] for desc in imp.get_suffixes() ]

# ZIP imports always search for .pyc AND .pyo, but reverse their order
# depending on the optimzation flag (-O).
ZIP_SEARCH_ORDER = [ '.py', '.pyc', '.pyo']
if not __debug__:
    ZIP_SEARCH_ORDER.remove('.pyc')
    ZIP_SEARCH_ORDER.append('.pyc')

try:
    # New in Python 2.5 (or setuptools 0.7+)
    from pkgutil import ImpImporter, ImpLoader, iter_importers, get_loader, \
         find_loader, iter_modules, get_importer
except ImportError:
    import marshal, inspect, re

    MODULE_TYPE_INFO = {}
    for suffix, mode, module_type in imp.get_suffixes():
        MODULE_TYPE_INFO[module_type] = (suffix, mode)

    class ImpImporter:
        """PEP 302 Importer that wraps Python's "classic" import algorithm

        ImpImporter(dirname) produces a PEP 302 importer that searches that
        directory.  ImpImporter(None) produces a PEP 302 importer that
        searches the current sys.path, plus any modules that are frozen or
        built-in.

        Note that ImpImporter does not currently support being used by
        placement on sys.meta_path.
        """

        def __init__(self, path=None):
            if path is not None:
                if not path:
                    path = '.'
                elif not os.path.isdir(path):
                    raise ImportError("not a directory")
            self.path = path

        def __repr__(self):
            return "<ImpImporter object %r>" % self.path

        def find_module(self, fullname, path=None):
            # Note: we ignore 'path' argument since it is only used via
            # meta_path
            subname = fullname.split(".")[-1]
            if subname != fullname and self.path is None:
                return None
            if self.path is None:
                path = None
            else:
                path = [os.path.realpath(self.path)]
            try:
                file, filename, etc = imp.find_module(subname, path)
            except ImportError:
                return None
            return ImpLoader(fullname, file, filename, etc)

        def iter_modules(self, prefix=''):
            if self.path is None or not os.path.isdir(self.path):
                return

            yielded = {}

            filenames = os.listdir(self.path)
            filenames.sort()  # handle packages before same-named modules

            for fn in filenames:
                modname = inspect.getmodulename(fn)
                if modname == '__init__' or modname in yielded:
                    continue

                path = os.path.join(self.path, fn)
                ispkg = False

                if not modname and os.path.isdir(path) and '.' not in fn:
                    modname = fn
                    for fn in os.listdir(path):
                        subname = inspect.getmodulename(fn)
                        if subname == '__init__':
                            ispkg = True
                            break
                    else:
                        continue    # not a package

                if modname and '.' not in modname:
                    yielded[modname] = 1
                    yield prefix + modname, ispkg
            return

    class ImpLoader:
        """PEP 302 Loader that wraps Python's "classic" import algorithm
        """
        code = None
        source = None

        def __init__(self, fullname, file, filename, etc):
            self.file = file
            self.filename = filename
            self.fullname = fullname
            self.etc = etc

        def load_module(self, fullname):
            self._reopen()
            try:
                mod = imp.load_module(fullname, self.file, self.filename,
                                      self.etc)
            finally:
                self.file.close()
            # Note: we don't set __loader__ because we want the module to
            # look normal; i.e. this is just a wrapper for standard import
            # machinery
            return mod

        def get_data(self, pathname):
            f = open(pathname, 'rb')
            try:
                data = f.read()
            finally:
                f.close()
            return data

        def _reopen(self):
            if self.file and self.file.closed:
                suffix, mode, module_type = self.etc
                self.file = open(self.filename, mode)
            return

        def _fix_name(self, fullname):
            if fullname is None:
                fullname = self.fullname
            elif fullname != self.fullname:
                raise ImportError("Loader for module %s cannot handle "
                                  "module %s" % (self.fullname, fullname))
            return fullname

        def _get_package_loader(self):
            return ImpImporter(self.filename).find_module('__init__')

        def is_package(self, fullname):
            fullname = self._fix_name(fullname)
            return self.etc[2] == imp.PKG_DIRECTORY

        def get_code(self, fullname=None):
            fullname = self._fix_name(fullname)
            if self.code is None:
                module_type = self.etc[2]
                if module_type == imp.PY_SOURCE:
                    source = self.get_source(fullname)
                    self.code = compile(source, self.filename, 'exec')
                elif module_type == imp.PY_COMPILED:
                    self._reopen()
                    try:
                        magic = self.file.read(4)
                        if magic == imp.get_magic():
                            timestamp = self.file.read(4)
                            self.code = marshal.load(self.file)
                    finally:
                        self.file.close()
                elif module_type == imp.PKG_DIRECTORY:
                    self.code = self._get_package_loader().get_code()
            return self.code

        def get_source(self, fullname=None):
            fullname = self._fix_name(fullname)
            if self.source is None:
                module_type = self.etc[2]
                if module_type == imp.PY_SOURCE:
                    self._reopen()
                    try:
                        self.source = self.file.read()
                    finally:
                        self.file.close()
                elif module_type == imp.PY_COMPILED:
                    suffix, mode = MODULE_TYPE_INFO[imp.PY_COMPILED]
                    filename = os.path.splitext(self.filename)[0] + suffix
                    if os.path.exists(filename):
                        f = open(filename, mode)
                        try:
                            self.source = f.read()
                        finally:
                            f.close()
                elif module_type == imp.PKG_DIRECTORY:
                    self.source = self._get_package_loader().get_source()
            return self.source

        def get_filename(self, fullname=None):
            fullname = self._fix_name(fullname)
            module_type = self.etc[2]
            if module_type == imp.PKG_DIRECTORY:
                return self._get_package_loader().get_filename()
            elif module_type in MODULE_TYPE_INFO:
                return self.filename
            return None

    def get_importer(path_item):
        """Retrieve a PEP 302 importer for the given path item
        """
        if sys.version < '2.3':
            importer = None
        else:
            try:
                importer = sys.path_importer_cache[path_item]
            except KeyError:
                for path_hook in sys.path_hooks:
                    try:
                        importer = path_hook(path_item)
                        break
                    except ImportError:
                        pass
                else:
                    importer = None
                sys.path_importer_cache.setdefault(path_item, importer)

        # The boolean values are used for caching valid and invalid
        # file paths for the built-in import machinery
        if importer in (None, True, False):
            try:
                importer = ImpImporter(path_item)
            except ImportError:
                importer = None
        return importer

    def iter_importers(fullname=''):
        if '.' in fullname:
            # Get the containing package's __path__
            pkg = '.'.join(fullname.split('.')[:-1])
            if pkg not in sys.modules:
                __import__(pkg)
            path = sys.modules[pkg].__path__
        else:
            # sys.meta_path is available in Python 2.3+
            for importer in getattr(sys, 'meta_path', []):
                yield importer
            path = sys.path
        for item in path:
            yield get_importer(item)
        if '.' not in fullname:
            yield ImpImporter()

    def get_loader(module_or_name):
        """Get a PEP 302 "loader" object for module_or_name

        If the module or package is accessible via the normal import
        mechanism, a wrapper around the relevant part of that machinery
        is returned.  Returns None if the module cannot be found or imported.
        If the named module is not already imported, its containing package
        (if any) is imported, in order to establish the package __path__.
        """
        if module_or_name in sys.modules:
            module_or_name = sys.modules[module_or_name]
        if isinstance(module_or_name, types.ModuleType):
            module = module_or_name
            loader = getattr(module, '__loader__', None)
            if loader is not None:
                return loader
            fullname = module.__name__
        else:
            fullname = module_or_name
        return find_loader(fullname)

    def find_loader(fullname):
        """Find a PEP 302 "loader" object for fullname

        If fullname contains dots, path must be the containing package's
        __path__. Returns None if the module cannot be found or imported.
        """
        for importer in iter_importers(fullname):
            loader = importer.find_module(fullname)
            if loader is not None:
                return loader
        return None

    def iter_zipimport_modules(importer, prefix):
        # make the path components regex safe
        sep = os.sep.replace('\\', '\\\\')
        path = prefix.replace(os.sep, sep)
        # using "non-greedy" matching in case a suffix is not just an
        # extension (like module.so for dlopen imports)
        modname = '[a-zA-Z_][a-zA-Z0-9_]*?'
        pkginit = sep + '__init__'
        suffix = '|'.join([ desc[0] for desc in imp.get_suffixes() ])
        suffix = suffix.replace('.', '\\.')
        pattern = '^%s(%s)(%s)?(%s)$' % (path, modname, pkginit, suffix)
        submodule_match = re.compile(pattern).match
        yielded = {}
        dirlist = list(importer._files)
        dirlist.sort()
        for fn in dirlist:
            match = submodule_match(fn)
            if match is not None:
                modname, pkginit, suffix = match.groups()
                if pkginit:
                    ispkg = True
                elif modname == '__init__':
                    continue
                else:
                    ispkg = False
                if modname not in yielded:
                    yielded[modname] = True
                    yield modname, ispkg
        return

    def iter_modules(path=None, prefix=''):
        """Yield submodule names+loaders for path or sys.path"""
        if path is None:
            importers = iter_importers()
        else:
            importers = map(get_importer, path)

        yielded = {}
        for importer in importers:
            if hasattr(importer, 'iter_modules'):
                modules = importer.iter_modules(prefix)
            elif isinstance(importer, zipimporter):
                modules = iter_zipimport_modules(importer, prefix)
            else:
                modules = []
            for name, ispkg in modules:
                if name not in yielded:
                    yielded[name] = 1
                    yield importer, name, ispkg
        return

try:
    from pkg_resources import get_provider, resource_filename
except ImportError:
    class DefaultProvider:
        """Resource provider for "classic" loaders"""
        def __init__(self, module):
            self.loader = getattr(module, '__loader__', None)
            self.module_path = os.path.dirname(module.__file__)

        def get_resource_filename(self, manager, resource_name):
            return self._fn(self.module_path, resource_name)

        def get_resource_stream(self, manager, resource_name):
            return open(self._fn(self.module_path, resource_name), 'rb')

        def get_resource_string(self, manager, resource_name):
            stream = self.get_resource_stream(manager, resource_name)
            try:
                return stream.read()
            finally:
                stream.close()

        def has_resource(self, resource_name):
            return self._has(self._fn(self.module_path, resource_name))

        def resource_isdir(self, resource_name):
            return self._isdir(self._fn(self.module_path, resource_name))

        def resource_listdir(self, resource_name):
            return self._listdir(self._fn(self.module_path, resource_name))

        def _fn(self, base, resource_name):
            return os.path.join(base, *resource_name.split('/'))

        def _has(self, pathname):
            return os.path.exists(pathname)

        def _isdir(self, pathname):
            return os.path.isdir(pathname)

        def _listdir(self, pathname):
            return os.listdir(pathname)

    class ZipProvider(DefaultProvider):
        """Resource provider for ZIP loaders"""

        _dirindex = None

        def __init__(self, module):
            DefaultProvider.__init__(self, module)
            self.zipinfo = self.loader._files
            self.zip_pre = self.loader.archive + os.sep

        def get_resource_filename(self, manager, resource_name):
            raise NotImplementedError("not supported by ZIP loaders")

        def get_resource_stream(self, manager, resource_name):
            data = self.get_resource_string(manager, resource_name)
            return cStringIO.StringIO(data)

        def get_resource_string(self, manager, resource_name):
            pathname = self._fn(self.module_path, resource_name)
            return self.loader.get_data(pathname)

        def _zipinfo_name(self, pathname):
            # Convert a virtual filename (full path to file) into a zipfile
            # subpath usable with the zipimport directory cache for our
            # target archive.
            if pathname.startswith(self.zip_pre):
                return pathname[len(self.zip_pre):]
            raise ValueError("%s not in %s" % (pathname, self.zip_pre))

        def _build_index(self):
            self._dirindex = index = {}
            for path in self.zipinfo:
                parts = path.split(os.sep)
                while parts:
                    parent = os.sep.join(parts[:-1])
                    if parent in index:
                        index[parent].append(parts[-1])
                        break
                    else:
                        index[parent] = [parts.pop()]
            return index

        def _has(self, pathname):
            arcname = self._zipinfo_name(fspath)
            return (arcname in self.zipinfo or
                    arcname in (self._dirindex or self._build_index()))

        def _isdir(self, pathname):
            arcname = self._zipinfo_name(pathname)
            return arcname in (self._dirindex or self._build_index())

        def _listdir(self, pathname):
            arcname = self._zipinfo_name(pathname)
            if arcname in (self._dirindex or self._build_index()):
                return self._dirindex[arcname][:]
            return []

    def get_provider(fullname):
        if fullname not in sys.modules:
            __import__(fullname)
        module = sys.modules[fullname]
        loader = getattr(module, '__loader__', None)
        if loader is None:
            provider = DefaultProvider(module)
        elif isinstance(loader, zipimporter):
            provider = ZipProvider(module)
        else:
            raise NotImplementedError('unsupported loader type: %s' % loader)
        return provider

    _resource_manager = None
else:
    # pkg_resources (aka setuptools) installed.; the resource_filename
    # top-level name is actually the bound method of the global
    # ResourceManager (at least that is what the PkgResources docs say).
    _resource_manager = resource_filename.im_self
    del resource_filename

GetImporter = get_importer
FindLoader = find_loader
IterModules = iter_modules

def FindImporter(fullname):
    """Find a PEP 302 "loader" object for fullname

    If fullname contains dots, path must be the containing package's
    __path__. Returns None if the module cannot be found or imported.
    """
    for importer in iter_importers(fullname):
        if importer.find_module(fullname) is not None:
            return importer
    return None

def GetLastModified(fullname):
    """
    Returns the last modified timestamp for the given module.
    """
    loader = get_loader(fullname)
    if hasattr(loader, 'get_filename'):
        suffixes = IMP_SEARCH_ORDER
    elif isinstance(loader, zipimporter):
        suffixes = ZIP_SEARCH_ORDER
    else:
        raise NotImplementedError("unsupported loader %s" % laoder)

    barename = '/' + fullname.replace('.', '/')
    if loader.is_package(fullname):
        barename += '/__init__'
    for suffix in suffixes:
        resource = barename + suffix
        try:
            timestamp = GetResourceLastModified(fullname, resource)
        except EnvironmentError:
            timestamp = 0
        else:
            break
    return timestamp

def GetSearchPath(fullname):
    loader = get_loader(fullname)
    if loader.is_package(fullname):
        if fullname in sys.modules:
            package = sys.modules[fullname]
        else:
            package = loader.load_module(fullname)
        return package.__path__
    return None

# -- Resource Handling ------------------------------------------------

def OsPathToResource(pathname):
    components = []
    for component in pathname.split(os.sep):
        if component == '..':
            del components[-1:]
        elif component not in ('', '.'):
            components.append(component)
    resource = '/'.join(components)
    if pathname.startswith(os.sep):
        resource = '/' + resource
    return resource

def NormalizeResource(package, resource):
    # normalize the resource pathname
    # Note, posixpath is not used as it doesn't remove leading '..'s
    components = []
    for component in resource.split('/'):
        if component == '..':
            del components[-1:]
        elif component not in ('', '.'):
            components.append(component)
    absolute = resource.startswith('/')
    resource = '/'.join(components)
    provider = get_provider(package)
    if absolute:
        # Find the provider for the distribution directory
        module_path = provider.module_path
        packages = package.split('.')
        if not get_loader(package).is_package(package):
            del packages[-1]
        for module in packages:
            module_path = os.path.dirname(module_path)
        provider.module_path = module_path
    return (provider, resource)

def GetResourceFilename(package, resource):
    """Returns a true filesystem name for the specified resource.
    """
    provider, resource = NormalizeResource(package, resource)
    return provider.get_resource_filename(_resource_manager, resource)

def GetResourceString(package, resource):
    """Return a string containing the contents of the specified resource.

    If the pathname is absolute it is retrieved starting at the path of
    the importer for 'fullname'.  Otherwise, it is retrieved relative
    to the module within the loader.
    """
    provider, resource = NormalizeResource(package, resource)
    return provider.get_resource_string(_resource_manager, resource)

def GetResourceStream(package, resource):
    """Return a readable stream for specified resource"""
    provider, resource = NormalizeResource(package, resource)
    return provider.get_resource_stream(_resource_manager, resource)

def GetResourceLastModified(package, resource):
    """Return a timestamp indicating the last-modified time of the
    specified resource.  Raises IOError is the pathname cannot be found
    from the loader for 'fullname'.
    """
    provider, resource = NormalizeResource(package, resource)
    if isinstance(provider.loader, zipimporter):
        if not resource:
            # it is the archive itself
            timestamp = os.stat(provider.module_path).st_mtime
        else:
            filename = provider._fn(provider.module_path, resource)
            zipinfo_name = provider._zipinfo_name(filename)
            try:
                dostime, dosdate = provider.zipinfo[zipinfo_name][5:7]
            except:
                import errno
                errorcode = errno.ENOENT
                raise IOError(errorcode, os.strerror(errorcode), zipinfo_name)
            timestamp = time.mktime((
                ((dosdate >> 9)  & 0x7f) + 1980, # tm_year
                ((dosdate >> 5)  & 0x0f) - 1,    # tm_mon
                ((dosdate >> 0)  & 0x1f),        # tm_mday
                ((dostime >> 11) & 0x1f),        # tm_hour
                ((dostime >> 5)  & 0x3f),        # tm_min
                ((dostime >> 0)  & 0x1f) * 2,    # tm_secs
                0, 0, -1))
    else:
        filename = provider.get_resource_filename(_resource_manager, resource)
        timestamp = os.stat(filename).st_mtime
    return timestamp
