########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Lib/ProgressIndicator.py,v 1.8 2005/04/18 23:17:57 jkloth Exp $
"""
Progress indicator

Copyright 2004 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

import sys, time, os

from Ft.Lib import Terminal

class ProgressIndicator:
    """
    A progress indicator intended for terminal output (relies on ^H).

    Indicator style, given as constructor argument, can be
    0: percentage; 1: bar; or 2: both. Default is 0.

    If using styles 1 or 2, an optional width argument
    for the bar portion can also be given (default 60).

    Example usage:
    # First emit whatever prefaces the indicator, if desired
    print " status:",
    sys.__stdout__.flush()
    # Create a new indicator
    p = ProgressIndicator(2)
    p.newIndicator()
    # With each iteration through a task, or as often as you want,
    # call updateProgress(), passing 2 numbers: amount completed,
    # and total amount to do.
    limit = 300000
    for i in range(limit):
        p.updateProgress(i, limit)
    print
    """

    if os.name == 'nt' or os.name == 'dos':
        # dark/light shades... thanks Oleg Broytmann.
        # OK for all MS-DOS codepages except 864 (Arabic) & 874 (Thai)
        # and python doesn't seem to mind writing the non-ASCII chars.
        _hashchar = '\xb2'
        _blankchar = '\xb0'
    elif (os.environ.get('LANG', '').endswith('.UTF-8') and
          os.environ.get('TERM') == "xterm"):
        # UTF-8 enabled terminal
        #  25% => x2591
        #  50% => x2592
        #  75% => x2593
        # 100% => x2588
        _hashchar = u'\u2588'.encode('UTF-8')
        _blankchar = u'\u2591'.encode('UTF-8')
    else:
        _hashchar = '*'
        _blankchar = ' '

    _current = 0
    _total = 0

    def __init__(self, prefix, stream=sys.stdout):
        if type(prefix) == type(u''):
            # avoid possible UnicodeError during output
            self.prefix = prefix.encode('ascii','replace')
        else:
            self.prefix = prefix
        self._tty = Terminal.Terminal(stream)
        self._writetty = self._tty.writetty
        self._flushtty = self._tty.flush
        return

    def newIndicator(self, total):
        """
        Start a new indicator at 00%.
        Optional style and width arguments are same as constructor.
        """
        self._current = 0
        self._total = total
        self._showProgress()
        return

    def _erase(self):
        self._writetty("\r")

    def message(self,message):
        # left-justify message within column width, padding or trimming as
        # required.
        columns = self._tty.columns()
        message = '%-*.*s' % (columns, columns, message)

        self._erase()
        self._writetty(message + '\n');
        self._showProgress()

    def updateProgress(self, cur):
        """
        Update an existing indicator to reflect given progress.
        Arguments are amount completed so far, and total to do.
        For example, if 4 out of 30 have been completed, call
        updateProgress(4,30).
        """
        self._current = cur
        self._erase()
        self._showProgress()
        return

    def _showProgress(self):
        barwidth = self._tty.columns() - 3 - len(self.prefix) - 4
        hashwidth = int(float(self._current+1)/self._total * (barwidth - 2))
        pct = int((self._current+1)*100/self._total)
        self._writetty("%s |%s%s %s%%" % (
            self.prefix,
            self._hashchar * hashwidth,
            self._blankchar * (barwidth - hashwidth - 2) + "|",
            " " * (pct < 100) + "%02d" % pct))
        self._flushtty()
        return


class AutoProgressIndicator(ProgressIndicator):
    def __init__(self, prefix, total, step=1, stream=sys.stdout):
        ProgressIndicator.__init__(self, prefix, stream)
        self.newIndicator(total)
        self._step = 1
        return

    def advance(self):
        self.updateProgress(self._current + self._step)
        return
