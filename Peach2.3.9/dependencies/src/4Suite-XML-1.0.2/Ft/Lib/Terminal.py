########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Lib/Terminal.py,v 1.6.4.1 2006/09/18 17:05:25 jkloth Exp $
"""
Provides some of the information from the terminfo database.

Copyright 2005 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

import os, re, sys

from Ft.Lib.Terminfo import TERMTYPES as _ANSITERMS
from Ft.Lib.Terminfo import DEFAULT_LINES as _LINES
from Ft.Lib.Terminfo import DEFAULT_COLUMNS as _COLUMNS

if sys.platform == 'win32':
    import msvcrt
    from Ft.Lib import _win32con
elif os.name == 'posix':
    _HAVE_TIOCGWINSZ = False
    try:
        import fcntl, termios, struct
    except ImportError:
        pass
    else:
        _HAVE_TIOCGWINSZ = hasattr(termios, 'TIOCGWINSZ')


# ISO 6429 color sequences are composed of sequences of numbers
# separated by semicolons.  The most common codes are:
#
#          0     to restore default color
#          1     for brighter colors
#          4     for underlined text
#          5     for flashing text
#         30     for black foreground
#         31     for red foreground
#         32     for green foreground
#         33     for yellow (or brown) foreground
#         34     for blue foreground
#         35     for purple foreground
#         36     for cyan foreground
#         37     for white (or gray) foreground
#         40     for black background
#         41     for red background
#         42     for green background
#         43     for yellow (or brown) background
#         44     for blue background
#         45     for purple background
#         46     for cyan background
#         47     for white (or gray) background


class AnsiEscapes:

    class Colors:
        DEFAULT = '\033[0m'
        BOLD = '\033[1m'

        FOREGROUND_BLACK = '\033[30m'
        FOREGROUND_MAROON = '\033[31m'
        FOREGROUND_GREEN = '\033[32m'
        FOREGROUND_BROWN = FOREGROUND_OLIVE = '\033[33m'
        FOREGROUND_NAVY = '\033[34m'
        FOREGROUND_PURPLE = '\033[35m'
        FOREGROUND_TEAL = '\033[36m'
        FOREGROUND_SILVER = '\033[37m'

        FOREGROUND_GRAY = '\033[1;30m'
        FOREGROUND_RED = '\033[1;31m'
        FOREGROUND_LIME = '\033[1;32m'
        FOREGROUND_YELLOW = '\033[1;33m'
        FOREGROUND_BLUE = '\033[1;34m'
        FOREGROUND_MAGENTA = FOREGROUND_FUCHSIA = '\033[1;35m'
        FOREGROUND_CYAN = FOREGROUND_AQUA = '\033[1;36m'
        FOREGROUND_WHITE = '\033[1;37m'

        BACKGROUND_BLACK = '\033[40m'
        BACKGROUND_MAROON = '\033[41m'
        BACKGROUND_GREEN = '\033[42m'
        BACKGROUND_BROWN = BACKGROUND_OLIVE = '\033[43m'
        BACKGROUND_NAVY = '\033[44m'
        BACKGROUND_PURPLE = '\033[45m'
        BACKGROUND_TEAL = '\033[46m'
        BACKGROUND_SILVER = '\033[47m'


# Methods/members a Terminal instance should expose from its underly stream.
_file_methods = ('flush', 'write', 'read', 'isatty', 'encoding')


class Terminal:

    def __init__(self, stream, keepAnsiEscapes=True):
        self._stream = stream
        for name in _file_methods:
            method = getattr(stream, name, None)
            if method is not None:
                setattr(self, name, method)

        if self.isatty():
            if sys.platform == 'win32':
                self._init_win32(stream, keepAnsiEscapes)
            elif os.name == 'posix' and os.environ.get('TERM') in _ANSITERMS:
                self._init_posix(stream, keepAnsiEscapes)
        return

    def _init_win32(self, stream, keepAnsiEscapes):
        # Apparently there exists an IDE where isatty() is True, but
        # the stream doesn't have a backing file descriptor.
        try:
            fileno = stream.fileno()
        except AttributeError:
            return
        # Get the Windows console handle of the file descriptor.
        try:
            self._handle = msvcrt.get_osfhandle(fileno)
        except IOError:
            return
        if keepAnsiEscapes:
            self._write_escape = self._escape_win32
            self._default_attribute = \
                _win32con.GetConsoleScreenBufferInfo(self._handle)[2]

        self.size = self._size_win32
        return

    def _init_posix(self, stream, keepAnsiEscapes):
        if keepAnsiEscapes:
            # stream handles ANSI escapes natively
            self.writetty = stream.write
        if _HAVE_TIOCGWINSZ:
            self.size = self._size_termios
        return

    def lines(self):
        return self.size()[0]

    def columns(self):
        return self.size()[1]

    def size(self):
        return (_LINES, _COLUMNS)

    # noop method for underlying streams which do not implement it
    def flush(self):
        return

    # noop method for underlying streams which do not implement it
    def write(self, str):
        return

    # noop method for underlying streams which do not implement it
    def read(self, size=-1):
        return ''

    # noop method for underlying streams which do not implement it
    def isatty(self):
        return False

    def close(self):
        # don't attempt to close a tty streams
        if self.isatty():
            return

        # ignore any errors closing the underlying stream
        try:
            self._stream.close()
        except:
            pass
        return

    # ANSI Set Display Mode: ESC[#;...;#m
    _ansi_sdm = re.compile('\033\\[([0-9]+)(?:;([0-9]+))*m')

    def writetty(self, bytes):
        start = 0
        match = self._ansi_sdm.search(bytes)
        while match is not None:
            # write everything up to the escape sequence
            self._stream.write(bytes[start:match.start()])

            # process the color codes
            self._write_escape(match.groups())

            # skip over the escape sequence
            start = match.end()

            # find the next sequence
            match = self._ansi_sdm.search(bytes, start)

        # write the remainder
        self._stream.write(bytes[start:])
        return

    def _write_escape(self, codes):
        """
        Escape function for handling ANSI Set Display Mode.

        Default behavior is to simply ignore the call (e.g. nothing is added
        to the output).
        """
        return

    # -- Terminal specific functions -----------------------------------

    def _size_termios(self):
        ws = struct.pack("HHHH", 0, 0, 0, 0)
        ws = fcntl.ioctl(self._stream.fileno(), termios.TIOCGWINSZ, ws)
        lines, columns, x, y = struct.unpack("HHHH", ws)
        return (lines, columns)

    def _escape_win32(self, codes):
        """Translates the ANSI color codes into the Win32 API equivalents."""

        # get the current text attributes for the stream
        size, cursor, attributes, window = \
              _win32con.GetConsoleScreenBufferInfo(self._handle)

        for code in map(int, filter(None, codes)):
            if code == 0: # normal
                # the default attribute
                attributes = self._default_attribute
            elif code == 1: # bold
                # bold only applies to the foreground color
                attributes |= _win32con.FOREGROUND_INTENSITY
            elif code == 30: # black
                attributes &= _win32con.BACKGROUND
            elif code == 31: # red
                attributes &= (_win32con.FOREGROUND_INTENSITY |
                               _win32con.BACKGROUND)
                attributes |= _win32con.FOREGROUND_RED
            elif code == 32: # green
                attributes &= (_win32con.FOREGROUND_INTENSITY |
                               _win32con.BACKGROUND)
                attributes |= _win32con.FOREGROUND_GREEN
            elif code == 33: # brown (bold: yellow)
                attributes &= (_win32con.FOREGROUND_INTENSITY |
                               _win32con.BACKGROUND)
                attributes |= (_win32con.FOREGROUND_RED |
                               _win32con.FOREGROUND_GREEN)
            elif code == 34: # blue
                attributes &= (_win32con.FOREGROUND_INTENSITY |
                               _win32con.BACKGROUND)
                attributes |= _win32con.FOREGROUND_BLUE
            elif code == 35: # purple (bold: magenta)
                attributes &= (_win32con.FOREGROUND_INTENSITY |
                               _win32con.BACKGROUND)
                attributes |= (_win32con.FOREGROUND_RED |
                               _win32con.FOREGROUND_BLUE)
            elif code == 36: # cyan
                attributes &= (_win32con.FOREGROUND_INTENSITY |
                               _win32con.BACKGROUND)
                attributes |= (_win32con.FOREGROUND_BLUE |
                               _win32con.FOREGROUND_GREEN)
            elif code == 37: # gray (bold: white)
                attributes &= (_win32con.FOREGROUND_INTENSITY |
                               _win32con.BACKGROUND)
                attributes |= (_win32con.FOREGROUND_RED |
                               _win32con.FOREGROUND_GREEN |
                               _win32con.FOREGROUND_BLUE)
            elif code == 40: # black
                attributes &= _win32con.FOREGROUND
            elif code == 41: # red
                attributes &= _win32con.FOREGROUND
                attributes |= _win32con.BACKGROUND_RED
            elif code == 42: # green
                attributes &= _win32con.FOREGROUND
                attributes |= _win32con.BACKGROUND_GREEN
            elif code == 43: # brown
                attributes &= _win32con.FOREGROUND
                attributes |= (_win32con.BACKGROUND_RED |
                               _win32con.BACKGROUND_GREEN)
            elif code == 44: # blue
                attributes &= _win32con.FOREGROUND
                attributes |= _win32con.BACKGROUND_BLUE
            elif code == 45: # purple
                attributes &= _win32con.FOREGROUND
                attributes |= (_win32con.BACKGROUND_RED |
                               _win32con.BACKGROUND_BLUE)
            elif code == 46: # cyan
                attributes &= _win32con.FOREGROUND
                attributes |= (_win32con.BACKGROUND_BLUE |
                               _win32con.BACKGROUND_GREEN)
            elif code == 47: # gray
                attributes &= _win32con.FOREGROUND
                attributes |= (_win32con.BACKGROUND_RED |
                               _win32con.BACKGROUND_GREEN |
                               _win32con.BACKGROUND_BLUE)

        _win32con.SetConsoleTextAttribute(self._handle, attributes)
        return

    def _size_win32(self):
        size, cursor, attributes, window = \
              _win32con.GetConsoleScreenBufferInfo(self._handle)
        left, top, right, bottom = window
        # use the buffer size for the column width as Windows wraps text
        # there instead of at the displayed window size
        columns, lines = size
        return (bottom - top, columns - 1)
