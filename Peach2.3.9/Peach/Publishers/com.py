
'''
Windows COM/DCOM/COM+ publishers.

@author: Michael Eddington
@version: $Id: com.py 2446 2011-07-04 13:37:25Z meddingt $
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

# $Id: com.py 2446 2011-07-04 13:37:25Z meddingt $

try:
	import time, sys, pywintypes, signal, os
	import win32com.client
	import win32com.client.gencache
except:
	pass
from Peach.publisher import Publisher

class Com(Publisher):
	"""
	Very simple Com publisher that allows for a single method call.  The
	method call is fed in as a string which is evaled.  This allows for
	calling any method with any number of parameters.
	"""
	
	_clsid = None
	_methodFormat = None
	_lastReturn = None
	_object = None
	
	def __init__(self, clsid):
		"""
		Create Com Object. clsid = '{...}'
		
		@type	clsid: string
		@param	clsid: CLSID of COM object in {...} format
		"""
		Publisher.__init__(self)
		self._clsid = clsid
		self.withNode = True
	
	def start(self):
		try:
			self._object = None
			self._object = win32com.client.DispatchEx(self._clsid)
			
		except pywintypes.com_error, e:
			print "Caught pywintypes.com_error creating ActiveX control [%s]" % e
			raise
			
		except:
			print "Caught unkown exception creating ActiveX control [%s]" % sys.exc_info()[0]
			raise
	
	def stop(self):
		self._object = None
	
#	def call(self, method, args):
	def callWithNode(self, method, args, argNodes):
		'''
		Call method on COM object.
		
		@type	method: string
		@param	method: Name of method to invoke
		@type	args: array of objects
		@param	args: Arguments to pass
		'''
		
		self._lastReturn = None
		
		realArgNodes = []
		for arg in argNodes:
			if len(arg) == 1:
				realArgNodes.append(arg[0])
			else:
				realArgNodes.append(arg)
		
		
		for arg in realArgNodes:
			print "Type", type(arg.getInternalValue())
			print "Value", repr(arg.getInternalValue())
		
		try:
			ret = None
			callStr = "ret = self._object.%s(" % str(method)
			
			if len(realArgNodes) > 0:
				for i in range(0, len(argNodes)):
					callStr += "realArgNodes[%d].getInternalValue()," % i
				
				callStr = callStr[:len(callStr)-1] + ")"
			
			else:
				callStr += ")"
			
			print "Call:", callStr
			
			exec callStr
			return ret
			
		except pywintypes.com_error, e:
			print "Caught pywintypes.com_error on call [%s]" % e
			raise
		
		except NameError, e:
			print "Caught NameError on call [%s]" % e
			raise
		
		except:
			print "Com::Call(): Caught unknown exception"
			raise
		
		return None
		
		
#	def property(self, property, value = None):
	def propertyWithNode(self, property, value, valueNode):
		'''
		Get or set property
		
		@type	property: string
		@param	property: Name of method to invoke
		@type	value: object
		@param	value: Value to set.  If None, return property instead
		'''
		
		try:
			if value == None:
				ret = None
				callStr = "ret = self._object.%s" % str(property)
				
				#print "Call string:", callStr
				exec callStr
				return ret
			
			ret = None
			callStr = "self._object.%s = valueNode.getInternalValue()" % str(property)
			
			#print "Call string:", callStr
			exec callStr
			return None
			
		except pywintypes.com_error, e:
			print "Caught pywintypes.com_error on property [%s]" % e
			#raise
		
		except NameError, e:
			print "Caught NameError on property [%s]" % e
			#raise
		
		except:
			print "Com::property(): Caught unknown exception"
			raise
		
		return None
		
# end

