from __future__ import generators
import os
import re
import sys
from distutils import sysconfig, util
from distutils.errors import DistutilsPlatformError
from xml.dom import pulldom
from xml.sax import make_parser

__all__ = ['GetConfigVars', 'NormalizePath', 'IterXml', 'FindIncludes']

_config_vars = None

def GetConfigVars(*args):
    """Parse the installed pyconfig.h file.

    A dictionary containing name/value pairs is returned.  If an
    optional dictionary is passed in as the second argument, it is
    used instead of a new dictionary.
    """
    global _config_vars
    if _config_vars is None:
        _config_vars = {}
        filename = sysconfig.get_config_h_filename()
        try:
            fp = open(filename)
        except IOError, err:
            msg = "invalid Python installation: unable to open %s" % filename
            if err.strerror:
                msg += " (%s)" % msg.strerror
            raise DistutilsPlatformError(msg)
        try:
            if sys.version < '2.5':
                define_rx = re.compile("#define ([A-Z][a-zA-Z0-9_]+) (.*)$")
                undef_rx = re.compile("/[*] #undef ([A-Z][a-zA-Z0-9_]+) [*]/$")
                line = fp.readline()
                while line:
                    m = define_rx.match(line)
                    if m:
                        n, v = m.group(1, 2)
                        try: v = int(v)
                        except ValueError: pass
                        _config_vars[n] = v
                    else:
                        m = undef_rx.match(line)
                        if m:
                            _config_vars[m.group(1)] = 0
                    line = fp.readline()
            else:
                sysconfig.parse_config_h(fp, _config_vars)
        finally:
            fp.close()

    if args:
        return [ _config_vars.get(name) for name in args ]
    return _config_vars


def NormalizePath(path):
    """Normalize a file/dir name for comparison purposes"""
    return os.path.normcase(os.path.realpath(path))


def IterXml(stream_or_string):
    if isinstance(stream_or_string, (str, unicode)):
        stream = open(stream_or_string)
    else:
        stream = stream_or_string
    parser = make_parser()
    stream = pulldom.DOMEventStream(stream, parser, pulldom.default_bufsize)
    event = stream.getEvent()
    while event:
        yield event
        event = stream.getEvent()
    return

_include_re = re.compile(r'\s*#\s*include\s*("|<)(?P<include>[^\1]+)(>|")')

def FindIncludes(source, include_dirs=None, includes=None):
    search_path = [os.path.dirname(source)]
    if include_dirs is not None:
        search_path.extend(include_dirs)
    if includes is None:
        includes = []
    f = open(util.convert_path(source))
    if sys.version < '2.3':
        iter_lines = f.readlines()
    else:
        iter_lines = f
    for line in iter_lines:
        match = _include_re.match(line)
        if match is not None:
            include = util.convert_path(match.group('include'))
            for path in search_path:
                filename = os.path.normpath(os.path.join(path, include))
                if os.path.isfile(filename) and filename not in includes:
                    includes.append(filename)
                    FindIncludes(filename, include_dirs, includes)
                    break
    f.close()
    return includes
