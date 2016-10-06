########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Lib/CommandLine/__init__.py,v 1.4 2004/08/06 04:57:08 mbrown Exp $
"""
Things to set up before importing other Ft.Lib.CommandLine modules

Copyright 2004 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

from Ft.Lib.Terminfo import GetColumns
CONSOLE_WIDTH = GetColumns()
del GetColumns

