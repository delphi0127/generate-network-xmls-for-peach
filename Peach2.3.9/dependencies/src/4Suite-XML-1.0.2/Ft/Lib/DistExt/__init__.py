########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Lib/DistExt/__init__.py,v 1.19.2.5 2006/10/30 20:39:16 jkloth Exp $
"""
Extensions to distutils to support building, installing, packaging 4Suite

Copyright 2005 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

# Make sure that we are using the proper version of Distutils
# We make certain assumptions about the implementation
def EnsureVersion(version):
    """Checks Distutils version against specified version number"""
    # We need to use LooseVersions because of distutils in Python 2.1
    try:
        import distutils
    except ImportError:
        raise ImportError('Requires distutils v%s or newer.\n'
                          'No distutils found.' % version)
    from distutils import __version__
    from distutils.version import LooseVersion
    dist_version = LooseVersion(__version__)
    expected = LooseVersion(version)
    if expected > dist_version:
        raise ImportError('Requires distutils v%s or newer.\n'
                          'Found version %s.' % (expected, dist_version))
    return
EnsureVersion('1.0.2')

# For convienence of script writers
from distutils.core import setup as _setup, DEBUG
from distutils.errors import DistutilsError
from distutils.extension import Extension
from Ft.Lib.DistExt import Structures
from Ft.Lib.DistExt.Structures import *

__all__ = ['EnsureVersion', 'Extension', 'setup']
__all__.extend(Structures.__all__)


def setup(**attrs):
    if 'distclass' not in attrs:
        from Ft.Lib.DistExt.PackageManager import PackageManager
        attrs['distclass'] = PackageManager
    # Only needed for Python 2.2
    try:
        return _setup(**attrs)
    except DistutilsError, error:
        if DEBUG: raise
        raise SystemExit('error: ' + str(error))
setup.__doc__ = _setup.__doc__


# -- Fixup various compatibility issues --------------------------------
import sys, os, re
from distutils import sysconfig, util

# Fix broken Mac OSX Jaguar Python
if sys.platform.startswith('darwin') and util.get_platform().endswith('-ppc'):
    cfgvars = sysconfig.get_config_vars()
    # The Makefile vars are already expanded, replace all uses of LDFLAGS
    for name in ('LDFLAGS', 'LDSHARED', 'BLDSHARED'):
        if cfgvars[name].find('-arch i386') != -1:
            cfgvars[name] = cfgvars[name].replace('-arch i386', '')
    del name, cfgvars

if sys.version < '2.3':
    # Make the announce method work the same for all versions.
    from distutils.cmd import Command
    def announce(self, msg, level=1):
        if level >= self.verbose:
            print msg
            sys.stdout.flush()
    Command.announce = announce
    del announce

    # Allow environment vars to override settings from the Makefile
    # (using version from Python 2.3)
    def customize_compiler(compiler):
        """Do any platform-specific customization of a CCompiler instance.

        Mainly needed on Unix, so we can plug in the information that
        varies across Unices and is stored in Python's Makefile.
        """
        if compiler.compiler_type == "unix":
            (cc, cxx, opt, basecflags, ccshared, ldshared, so_ext) = \
                sysconfig.get_config_vars('CC', 'CXX', 'OPT', 'BASECFLAGS',
                        'CCSHARED', 'LDSHARED', 'SO')

            if os.environ.has_key('CC'):
                cc = os.environ['CC']
            if os.environ.has_key('CXX'):
                cxx = os.environ['CXX']
            if os.environ.has_key('CPP'):
                cpp = os.environ['CPP']
            else:
                cpp = cc + " -E"           # not always
            if os.environ.has_key('LDFLAGS'):
                ldshared = ldshared + ' ' + os.environ['LDFLAGS']
            if basecflags:
                opt = basecflags + ' ' + opt
            if os.environ.has_key('CFLAGS'):
                opt = opt + ' ' + os.environ['CFLAGS']
                ldshared = ldshared + ' ' + os.environ['CFLAGS']
            if os.environ.has_key('CPPFLAGS'):
                cpp = cpp + ' ' + os.environ['CPPFLAGS']
                opt = opt + ' ' + os.environ['CPPFLAGS']
                ldshared = ldshared + ' ' + os.environ['CPPFLAGS']

            cc_cmd = cc + ' ' + opt
            compiler.set_executables(
                preprocessor=cpp,
                compiler=cc_cmd,
                compiler_so=cc_cmd + ' ' + ccshared,
                linker_so=ldshared,
                linker_exe=cc)

            compiler.shared_lib_extension = so_ext
    sysconfig.customize_compiler = customize_compiler
    del customize_compiler

    def get_python_version():
        return sys.version[:3]
    sysconfig.get_python_version = get_python_version
    del get_python_version

# -- Monkey-patch filelist pattern matching
from distutils import filelist
if sys.platform == 'win32':
    _special_chars = r'<>:"/\\|'
else:
    _special_chars = r'/'
def glob_to_re(pat, _specials=_special_chars):
    i, n = 0, len(pat)
    res = ''
    while i < n:
        c = pat[i]
        i = i+1
        if c == '*':
            res = res + '[^%s]*' % _specials
        elif c == '?':
            res = res + '[^%s]' % _specials
        elif c == '[':
            j = i
            if j < n and pat[j] == '!':
                j = j+1
            if j < n and pat[j] == ']':
                j = j+1
            while j < n and pat[j] != ']':
                j = j+1
            if j >= n:
                res = res + '\\['
            else:
                stuff = pat[i:j].replace('\\','\\\\')
                i = j+1
                if stuff[0] == '!':
                    stuff = '^' + stuff[1:]
                elif stuff[0] == '^':
                    stuff = '\\' + stuff
                res = '%s[%s]' % (res, stuff)
        else:
            res = res + re.escape(c)
    return res + "$"
filelist.glob_to_re = glob_to_re
del glob_to_re
