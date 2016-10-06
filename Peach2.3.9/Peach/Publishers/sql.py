
'''
SQL publisher objects.  Includes a default ODBC publisher.

@author: Michael Eddington
@version: $Id: sql.py 2020 2010-04-14 23:13:14Z meddingt $
'''

#
# Copyright (c) Michael Eddington
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

# $Id: sql.py 2020 2010-04-14 23:13:14Z meddingt $

from types import *

import sys
try:
	import dbi, odbc
except:
	pass

from Peach.publisher import Publisher

#__all__ = ["Odbc"]

class Odbc(Publisher):
	'''
	Publisher for ODBC connections.  Generated data sent as a SQL query via
	execute.  Calling receave will return a string of all row data concatenated
	together with \t as field separator.
	
	Currently this Publisher makes use of the odbc package which is some what
	broken in that you must create an actual ODBC DSN via the ODBC manager.  
	Check out mxODBC which is not open source for another alterative.
	
	Note:  Each call to start/stop will create and close the SQL connection and
	cursor.
	'''
	
	def __init__(self, dsn):
		'''
		@type	dsn: string
		@param	dsn: DSN must be in format of "dsn/user/password" where DSN is a DSN name.
		'''
		Publisher.__init__(self)
		self._dsn = dsn
		self._sql = None
		self._cursor = None
		self._sql = None
	
	def start(self):
		'''
		Create connection to server.
		'''
		self._sql = odbc.odbc(self._dsn)
	
	def stop(self):
		'''
		Close any open cursors, and close connection to server.
		'''
		self._cursor.close()
		self._cursor = None
		self._sql.close()
		self._sql = None
	
	def call(self, method, args):
		'''
		Create cursor and execute data.
		'''
		self._cursor = self._sql.cursor()
		
		try:
			self._cursor.execute(method, args)
		except:
			print "Warning: execute failed: ", sys.exc_info()
			pass
		
		ret = ''
		try:
			row = self._cursor.fetchone()
			for i in range(len(row)):
				retType = type(row[i])
				if retType is IntType:
					ret += "\t%d" % row[i]
				elif retType is FloatType:
					ret += "\t%f" % row[i]
				elif retType is LongType:
					ret += "\t%d" % row[i]
				elif retType is StringType:
					ret += "\t%s" % row[i]
		
		except:
			pass
		
		return ret

# end

