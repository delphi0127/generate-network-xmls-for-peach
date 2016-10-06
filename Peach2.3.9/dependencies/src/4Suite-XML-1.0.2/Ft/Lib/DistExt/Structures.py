"""
Data structures that are to be used in a pkg file.
"""

from distutils.errors import DistutilsSetupError

__all__ = ['Localization', 'FileList', 'Script', 'Executable',
           'File', 'ModulesDocument', 'ExtensionsDocument', 'Document']

# -- utility functions for verifying values to constructors ------------

def _string_check(arg):
    return isinstance(arg, str)

def _string_sequence_check(arg):
    return (isinstance(arg, (list, tuple)) and
            reduce(lambda a, b: a + isinstance(b, str), arg, 0) == len(arg))

# -- class for the l10n parameter to distribution ----------------------

class Localization:
    """Defines a message catalog for a particular language"""
    def __init__(self, language, source):
        # Verify the values
        assert _string_check(language), "'language' must be a string"
        assert _string_check(source), "'source' must be a string"

        # Store the values
        self.language = language
        self.source = source

    def __repr__(self):
        return 'Localization(%r, %r)' % (self.language, self.source)

# -- class for the l10n parameter to distribution ----------------------

from distutils import filelist
class FileList(filelist.FileList):
    """
    Defines a collection of files.
    """
    def __init__(self, dest, sources, recursive=False, excludes=None):
        filelist.FileList.__init__(self)
        assert _string_check(dest), "'dest' must be a string"
        assert _string_sequence_check(sources), \
               "'sources' must be a sequence of strings"
        self.dest = dest
        self.sources = sources
        self.recursive = recursive
        self.excludes = excludes or ()
        return

# -- classes for the scripts parameter to distribution -----------------

class Script:
    def __init__(self, name, module, function=None, application=None):
        assert _string_check(name), "'name' must be a string"
        assert _string_check(module), "'module' must be a string"
        assert function is None or _string_check(function), \
            "'function' must be a string or None"
        assert application is None or _string_check(application), \
            "'application' must be a string or None"
        if function is not None and application is not None:
            raise DistutilsSetupError(
                "only one of 'function' or 'application' allowed")
        elif function is None and application is None:
            raise DistutilsSetupError(
                "one of 'function' or 'application' is required")
        elif application:
            function = application + '.main'

        self.name = name
        self.module = module
        self.function = function
        self.application = application

    def __repr__(self):
        return 'Script(%r, %r, %r, %r)' % (
            self.name, self.module, self.function, self.application)


class Executable:
    """
    Just a collection of attributes that describes an executable
    and everything needed to build it (hopefully in a portable way,
    but there are hooks that let you be as unportable as you need).

    Instance attributes:
      name : string
        the full name of the extension, including any packages -- ie.
        *not* a filename or pathname, but Python dotted name
      sources : [string]
        list of source filenames, relative to the distribution root
        (where the setup script lives), in Unix form (slash-separated)
        for portability.  Source files may be C, C++, SWIG (.i),
        platform-specific resource files, or whatever else is recognized
        by the "build_ext" command as source for a Python extension.
      include_dirs : [string]
        list of directories to search for C/C++ header files (in Unix
        form for portability)
      define_macros : [(name : string, value : string|None)]
        list of macros to define; each macro is defined using a 2-tuple,
        where 'value' is either the string to define it to or None to
        define it without a particular value (equivalent of "#define
        FOO" in source or -DFOO on Unix C compiler command line)
      undef_macros : [string]
        list of macros to undefine explicitly
      library_dirs : [string]
        list of directories to search for C/C++ libraries at link time
      libraries : [string]
        list of library names (not filenames or paths) to link against
      runtime_library_dirs : [string]
        list of directories to search for C/C++ libraries at run time
        (for shared extensions, this is when the extension is loaded)
      extra_objects : [string]
        list of extra files to link with (eg. object files not implied
        by 'sources', static library that must be explicitly specified,
        binary resource files, etc.)
      extra_compile_args : [string]
        any extra platform- and compiler-specific information to use
        when compiling the source files in 'sources'.  For platforms and
        compilers where "command line" makes sense, this is typically a
        list of command-line arguments, but for other platforms it could
        be anything.
      extra_link_args : [string]
        any extra platform- and compiler-specific information to use
        when linking object files together to create the extension (or
        to create a new static Python interpreter).  Similar
        interpretation as for 'extra_compile_args'.
    """

    def __init__ (self, name, sources,
                  include_dirs=None,
                  define_macros=None,
                  undef_macros=None,
                  library_dirs=None,
                  libraries=None,
                  runtime_library_dirs=None,
                  extra_objects=None,
                  extra_compile_args=None,
                  extra_link_args=None,
                 ):

        assert _string_check(name), "'name' must be a string"
        assert _string_sequence_check(sources), \
               "'sources' must be a sequence of strings"

        self.name = name
        self.sources = sources
        self.include_dirs = include_dirs or []
        self.define_macros = define_macros or []
        self.undef_macros = undef_macros or []
        self.library_dirs = library_dirs or []
        self.libraries = libraries or []
        self.runtime_library_dirs = runtime_library_dirs or []
        self.extra_objects = extra_objects or []
        self.extra_compile_args = extra_compile_args or []
        self.extra_link_args = extra_link_args or []
        return

    def __repr__(self):
        return 'Executable(%r, %r)' % (self.name, self.sources)

# -- classes for the doc_files parameter to the distribution -----------


class File:
    """
    A collection of attributes that describes a file on the filesystem.
    Instances of File are used as members of the doc_files argument to
    setup().
    """
    def __init__(self, source, outdir='', flags=None):
        assert _string_check(source), "'source' must be a string"
        assert _string_check(outdir), "'outdir' must be a string"

        self.source = source
        self.outdir = outdir
        self.flags = flags or []
        return

    def get_source_files(self):
        return [self.source]

    def __repr__(self):
        return '%s(%r, %r, %r)' % (self.__class__.__name__,
                                   self.source, self.outdir, self.flags)


class GeneratedDocument:
    def get_source_files(self):
        # The modules are assumed to be installed elsewhere
        return []


class ModulesDocument(GeneratedDocument):
    def __init__(self, title, packages):
        assert _string_check(title), "'title' must be a string"
        assert _string_sequence_check(packages), \
               "'packages' must be a sequence of strings"

        self.title = title
        self.packages = packages

        # Filled in later by build_docs
        self.modules = []
        return

    def __repr__(self):
        return '%s(%r, %r)' % (self.__class__.__name__,
                               self.title, self.packages)


class ExtensionsDocument(GeneratedDocument):
    """
    A collection of attributes that describes a set of Python modules that
    implement 4Suite's XPath/XSLT extension API. Instances of File are
    used as members of the doc_files argument to setup().
    """
    def __init__(self, name, modules, title):
        assert _string_check(name), "'name' must be a string"
        assert _string_sequence_check(modules), \
               "'modules' must be a sequence of strings"
        assert _string_check(title), "'title' must be a string"

        self.name = name
        self.modules = modules
        self.title = title
        return

    def __repr__(self):
        return '%s(%r, %r, %r)' % (self.__class__.__name__,
                                   self.name, self.modules, self.title)


class Document:
    """
    An XSLT rendered document. It creates both a XML, HTML and Text version
    of the document (if desired)
    """
    def __init__(self, source, stylesheet, params=None, title=None,
                 category=None, flags=None, mtime=None, outfile=None):
        assert _string_check(source), "'source' must be a string"
        assert _string_check(stylesheet), "'stylesheet' must be a string"

        self.source = source
        self.stylesheet = stylesheet
        self.params = params or {}
        self.title = title or ''
        self.category = category or 'general'
        self.flags = flags or []
        self.mtime = mtime
        self.outfile = outfile

    def __repr__(self):
        return 'Document(%r, %r, %r, %r, %r, %r, %r, %r)' % (
            self.source, self.stylesheet, self.params, self.title,
            self.category, self.flags, self.mtime, self.outfile)
