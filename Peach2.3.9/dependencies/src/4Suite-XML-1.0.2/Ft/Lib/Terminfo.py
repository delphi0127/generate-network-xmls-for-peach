########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Lib/Terminfo.py,v 1.6 2005/11/15 07:36:24 mbrown Exp $
"""
Provides some of the information from the terminfo database.

Copyright 2005 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

import sys, os

TERMTYPES = ['linux', 'console', 'con132x25', 'con132x30', 'con132x43',
             'con132x60', 'con80x25', 'con80x28', 'con80x30', 'con80x43',
             'con80x50', 'con80x60', 'xterm', 'xterm-color', 'color-xterm',
             'vt100', 'vt100-color', 'rxvt', 'ansi', 'Eterm', 'putty',
             'vt220-color', 'cygwin'
             ]

# Default sizes should fit on all displays.
DEFAULT_LINES = 24
DEFAULT_COLUMNS = 80

def GetLines(stream=sys.stdout):
    lines = DEFAULT_LINES
    if hasattr(stream, 'isatty') and stream.isatty() \
        and os.environ.get('TERM') in TERMTYPES:
        try:
            import fcntl, termios, struct
        except ImportError:
            pass
        else:
            if hasattr(termios, 'TIOCGWINSZ'):
                ws = struct.pack("HHHH", 0, 0, 0, 0)
                ws = fcntl.ioctl(stream.fileno(), termios.TIOCGWINSZ, ws)
                lines, columns, x, y = struct.unpack("HHHH", ws)
    return lines

def GetColumns(stream=sys.stdout):
    columns = DEFAULT_COLUMNS
    if stream.isatty() and os.environ.get('TERM') in TERMTYPES:
        try:
            import fcntl, termios, struct
        except ImportError:
            pass
        else:
            if hasattr(termios, 'TIOCGWINSZ'):
                ws = struct.pack("HHHH", 0, 0, 0, 0)
                ws = fcntl.ioctl(stream.fileno(), termios.TIOCGWINSZ, ws)
                lines, columns, x, y = struct.unpack("HHHH", ws)
    return columns
