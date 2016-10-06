
'''
Shared library publisher.

@author: Michael Eddington
@version: $Id$
'''

#
# Copyright (c) 2008 Michael Eddington
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

# $Id$

import time, sys, ctypes, signal, os
from Peach.publisher import Publisher

class Dll(Publisher):
	"""
	Shared library publisher using ctypes
	"""
	
	def __init__(self, library):
		Publisher.__init__(self)
		self.library = library
		self.dll = None
		self.withNode = True
	
	def start(self):
		try:
			self.dll = ctypes.cdll.LoadLibrary(self.library)
			
		except:
			print "Caught exception loading library [%s]" % self.library
			raise
	
	def stop(self):
		self.dll = None
	
	def callWithNode(self, method, args, argNodes):
		'''
		Call method on COM object.
		
		@type	method: string
		@param	method: Name of method to invoke
		@type	args: array of objects
		@param	args: Arguments to pass
		'''
		
		self._lastReturn = None
		
		#ct = argNodes[0].asCType()
		#print ct
		#print ct.contents
		#print ct._fields_
		#print ct.Named_37
		#print ct.Named_38
		
		try:
			ret = None
			callStr = "self.dll.%s(" % str(method)
			
			if len(args) > 0:
				for i in range(0, len(args)):
					callStr += "argNodes[%d].asCType()," % i
				
				callStr = callStr[:len(callStr)-1] + ")"
			
			else:
				callStr += ")"
			
			ret = eval(callStr)
			return ret
			
		except:
			print "dll.Dll(): Caught unknown exception making call to %s" % method
			raise
		
		return None
		
	#def property(self, property, value = None):
	#	'''
	#	Get or set property
	#	
	#	@type	property: string
	#	@param	property: Name of method to invoke
	#	@type	value: object
	#	@param	value: Value to set.  If None, return property instead
	#	'''
	#	
	#	try:
	#		if value == None:
	#			ret = None
	#			callStr = "ret = self._object.%s" % str(property)
	#			
	#			#print "Call string:", callStr
	#			exec callStr
	#			return ret
	#		
	#		ret = None
	#		callStr = "self._object.%s = value" % str(property)
	#		
	#		#print "Call string:", callStr
	#		exec callStr
	#		return None
	#		
	#	except pywintypes.com_error, e:
	#		print "Caught pywintypes.com_error on property [%s]" % e
	#		#raise
	#	
	#	except NameError, e:
	#		print "Caught NameError on property [%s]" % e
	#		#raise
	#	
	#	except:
	#		print "Com::property(): Caught unknown exception"
	#		raise
	#	
	#	return None
		
# end

