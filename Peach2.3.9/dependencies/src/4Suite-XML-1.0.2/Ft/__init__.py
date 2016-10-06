########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/__init__.py,v 1.49.2.3 2006/09/14 20:52:02 jkloth Exp $
"""
4Suite: an open-source platform for XML and RDF processing.

Copyright 2004 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

__all__ = ['DEFAULT_ENCODING', 'MAX_PYTHON_RECURSION_DEPTH', '__version__',
           'FtException', 'FtWarning', 'GetConfigVars', 'GetConfigVar',
           'TranslateMessage']

# True/False did not appear until Python 2.2.1
import sys
if sys.version < '2.2.1':
    raise ImportError('4Suite requires Python 2.2.1 or newer.')

# PYTHONCASEOK is an environment variable that causes imports to
# treat module names case-insensitively on certain file systems,
# which is dangerous in 4Suite since we may have modules with the
# same names (when compared case-insensitively) as stdlib modules.
# We can't be sure which file system type is in use, so we can't
# restrict this check to certain platforms. See PEP 235.
import os
if 'PYTHONCASEOK' in os.environ:
    raise ImportError('4Suite requires case-sensitive imports;'
                      ' unset PYTHONCASEOK environment variable.')

# Frozen executables do not properly initialize the codecs module as their
# import hooks are not installed when it is loaded. See Python/pythonrun.c
# in a Python source distribution for the relevant code in Py_Initialize().
if getattr(sys, 'frozen', False):
    import encodings

# Get the encoding that the user is likely using.
import locale
try:
    # getpreferredencoding() new in Python 2.3+
    encoding = locale.getpreferredencoding()
except locale.Error:
    # Unable to set locale; use the current settings.
    encoding = locale.getpreferredencoding(False)
except AttributeError:
    if sys.platform in ('win32', 'darwin', 'mac'):
        # On Windows, this will return the ANSI code page;
        # On Mac, this should return the system encoding.
        encoding = locale.getdefaultlocale()[1]
    elif hasattr(locale, 'CODESET'):
        # CODESET requires that nl_langinfo() also exists.
        encoding = locale.nl_langinfo(locale.CODESET)
    else:
        # fall back to parsing environment variables
        encoding = locale.getdefaultlocale()[1]
DEFAULT_ENCODING = encoding or 'US-ASCII'

#10,000 is the value from Python 1.5.2
MAX_PYTHON_RECURSION_DEPTH = 10000


class FtException(Exception):
    """
    Base class for all 4Suite-specific exceptions
    """
    #FIXME: make all exception classes use *args instead of argtuple
    def __init__(self, errorCode, messages, argtuple=(), **kwargs):
        """
        errorCode = Numeric ID for the type of error.
        messages = Mapping of errorCodes to localized error message strings.
        argtuple or keyword args = Values for message string formatting.
        """
        assert not (argtuple and kwargs) # we can use args or kwargs, not both
        self.message = messages[errorCode] % (kwargs or argtuple)
        self.errorCode = errorCode
        # Exception.__init__() will set self.args to the args passed to it
        Exception.__init__(self, self.message, (kwargs or argtuple))

    def __getattr__(self, name):
        if name == 'params':
            return self.args[1]
        raise AttributeError(name)

    def __str__(self):
        return self.message

    def __repr__(self):
        return '%s: %s' % (self.__class__.__name__, self.message)


class FtWarning(Warning):
    """
    Base class for all 4Suite-specific warnings.
    """
    pass


# Install our warnings display hook for 4Suite warnings only if it is not
# already installed. That would be the case during a reload().
# Python 2.2 doesn't support __module__ on functions, use the function globals
# instead to find it.
import warnings
if getattr(warnings.showwarning, '__module__',
           warnings.showwarning.func_globals['__name__']) == __name__:
    __showwarning = warnings.showwarning
else:
    def __showwarning(message, category, filename, lineno, file=None):
        """
        warnings.showwarning() replacement that word-wraps the message if
        file is a terminal, and doesn't add filename, line, stack info to
        FtWarnings.
        """
        if issubclass(category, FtWarning):
            from Ft.Lib import Wrap, Terminal
            if file is None:
                file = sys.stderr
            terminal = Terminal.Terminal(file)
            message = "%s: %s\n" % (category.__name__, message)
            if terminal.isatty():
                message = Wrap(message, terminal.columns())
            terminal.writetty(message)
            terminal.flush()
        else:
            __showwarning.__base__(message, category, filename, lineno, file)
        return
    # Save a reference to the original to use for non-4Suite warnings
    __showwarning.__base__ = warnings.showwarning
    # Install our replacement function
    warnings.showwarning = __showwarning


# Load the installation information module, only available from installed
# 4Suite or during setup via dummy module.
try:
    import __config__
except ImportError:
    from distutils.fancy_getopt import wrap_text

    msg = """
4Suite is having trouble importing the modules it needs.
This is usually because the current working directory, which happens
to be %r at the moment, contains modules with names that are the
same as modules that 4Suite is trying to import. For example, 4Suite
cannot be invoked from the source code directory that contains the
setup.py that was used to install 4Suite.

Try changing the current working directory to a suitable location
outside of the 4Suite source. If you continue to have trouble,
please send a message to the 4Suite mailing list at
4suite@lists.fourthought.com, along with any information that might
explain why you got this message.
""" % os.getcwd()

    # Wrap the message to 78 characters preserving paragraphs
    lines = []
    for chunk in msg.split('\n\n'):
        lines.extend(wrap_text(chunk, 78))
        lines.append('')
    raise SystemExit('\n'.join(lines))


def GetConfigVars(*names):
    """
    With no arguments, return a dictionary of all configuration variables
    relevant for the current installation.  With arguments, return a list
    of values that result from looking up each argument in the configuration
    variable dictionary.

    The following are the currently defined variables and their meaning:

    NAME, FULLNAME, VERSION, URL - fields as given for call to setup()
    BINDIR - directory for user executables
    DATADIR - directory for read-only platform-independent data
    LIBDIR - directory for extra libraries
    LOCALEDIR - directory for message catalogs
    LOCALSTATEDIR - directory for modifiable host-specific data
    SYSCONFIDIR - directory for read-only host-specific data
    """
    if names:
        vals = []
        for name in names:
            vals.append(getattr(__config__, name, None))
        return vals
    else:
        return vars(__config__)


def GetConfigVar(name):
    """
    Return the value of a single variable using the dictionary returned
    by 'get_config_vars()'.  Equivalent to GetConfigVars().get(name)
    """
    return getattr(__config__, name, None)

__version__ = __config__.VERSION

from Ft.Lib import Gettext
if getattr(__config__, 'RESOURCEBUNDLE', False):
    bundle = __name__
else:
    bundle = None
translation = Gettext.GetTranslation(__config__.NAME, __config__.LOCALEDIR,
                                     fallback=True, bundle=bundle)
TranslateMessage = translation.gettext
TranslateMessagePlural = translation.ngettext

# This *MUST* be the last thing done so that the module namespace reflects
# all of the above when using Python Eggs.
try:
    import pkg_resources
except ImportError:
    pass
else:
    try:
        pkg_resources.get_distribution(__config__.NAME)
    except pkg_resources.DistributionNotFound:
        pass
    else:
        pkg_resources.declare_namespace(__name__)
        sys.modules[__name__].__dict__.update(globals())
