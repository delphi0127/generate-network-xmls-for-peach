
'''
Implementation of base Transformer class.

@author: Michael Eddington
@version: $Id: transformer.py 872 2008-05-12 17:56:54Z meddingt $
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

# $Id: transformer.py 872 2008-05-12 17:56:54Z meddingt $

class Fixup:
	'''
	Fixup of values in the data model.  This is done using by keeping
	an internal list of references that can be resolved during
	fixup().  Helper functions are provided in this base class for
	resolving elements in the data model.
	'''
	
	def __init__(self):
		'''
		Create fixup object
		'''
		self.context = None
		self.isInSelf = False
	
	def dofixup(self):
		'''
		Wrapper around fixup() to prevent endless recurtion.  Please
		do not override me :)
		'''
		
		if not self.isInSelf:
			try:
				self.isInSelf = True
				return self.fixup()
			finally:
				self.isInSelf = False
			
		else:
			return None
		
	def _getRef(self):
		'''
		AFtering incoming data is cracked some elements move around.
		Peach will auto update parameters called "ref" but you will
		need to-refetch the value using this method.
		'''
		for param in self.context.fixup:
			if param.name == "ref":
				return eval(param.defaultValue)
		
		return None
	
	def fixup(self):
		'''
		Perform the required fixup.  OVERRIDE ME!
		'''
		
		raise Exception("Error: Fixup not implemented yet!")
	
	def _findDataElementByName(self, name):
		'''
		DEPRICATED!
		
		Use self.context.findDataElementByName(name) instead!
		
		Internal helper method that will locate a data element in
		the data model by it's name.  We will search starting at
		our current data element's node level and look down then
		up for the requested node.
		
		To be more specific about a node you can use the dotted
		name "Element1.ELement2".
		'''
		
		if self.context == None:
			raise Exception("Error: Fixup tried to use _findDataElementByName but we have no context!")
		
		return self.context.findDataElementByName(name)
	
	def _getContextRoot(self):
		'''
		DEPRICATED!
		
		Use self.context.getRootOfDataMap() instead!
		
		Inernal helper method that returns the root of the current
		data model.
		'''
		
		return self.context.getRootOfDataMap()
		

# end
