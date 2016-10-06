
'''
No-console window wrapper for PeachGui

@author: Michael Eddington
@version: $Id: peachbuilder.pyw 1785 2009-06-24 07:26:59Z meddingt $
'''

#
# Copyright (c) 2007-2008 Michael Eddington
#
# Permission is hereby granted, free of charge, to any person obtaining a copy 
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights 
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
# copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in	
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

# Authors:
#   Michael Eddington (mike@phed.org)

# $Id: peachbuilder.pyw 1785 2009-06-24 07:26:59Z meddingt $

import sys,os

# SPEED ME UP SCOTTY!
#if sys.version.find("AMD64") == -1:
#	import psyco
#	psyco.full()

from Peach.Gui import PeachGui

# Chdir so we can locate our icons
if not (hasattr(sys,"frozen") and sys.frozen == "windows_exe"):
	os.chdir( sys.path[0] + "/peach/gui" )
else:
	os.chdir(os.path.dirname(os.path.abspath(sys.executable)))

PeachGui.RunPeachEditor()

# end
