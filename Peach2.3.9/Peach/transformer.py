
'''
Implementation of base Transformer class.

@author: Michael Eddington
@version: $Id: transformer.py 2020 2010-04-14 23:13:14Z meddingt $
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

# $Id: transformer.py 2020 2010-04-14 23:13:14Z meddingt $

class Transformer(object):
	'''
	Transforms some form of input.  Transformers can be changed.
	Base64 encoding would be a type of Transformer.  Chained transformer
	run *after* this transformer.
	'''
	
	def __init__(self, anotherTransformer = None):
		'''
		Create Transformer object.
		
		@type	anotherTransformer: Transformer
		@param	anotherTransformer: A transformer to run next
		'''
		self._anotherTransformer = anotherTransformer
	
	def changesSize(self):
		'''
		Does this transformer return data that could be
		a different size then seed?
		'''
		return True
	
	def transform(self, data):
		'''
		Transform data in some mannor.  Will then call next
		transformer in chain if specified.
		
		@type	data: string
		@param	data: Data to transform
		@rtype: string
		@return transformed data
		'''
		print "Warning: Transformer.transform() is depricated.  Please update your code to use encode/decode."
		return self.encode(data)
	
	def encode(self, data):
		'''
		Transform data in some mannor.  Will then call next
		transformer in chain if specified.
		
		@type	data: string
		@param	data: Data to transform
		@rtype: string
		@return transformed data
		'''
		ret = self.realEncode(data)
		
		if self._anotherTransformer != None:
			return self._anotherTransformer.encode(ret)
		
		return ret
	
	def decode(self, data):
		'''
		Perform reverse transformation if possible.
		
		@type	data: string
		@param	data: Data to transform
		@rtype: string
		@return transformed data
		'''
		
		if self._anotherTransformer != None:
			data = self._anotherTransformer.decode(data)
		
		return self.realDecode(data)
	
	def getAnotherTransformer(self):
		'''
		Gets the next transformer in the chain.  This transformer
		will be called *after* this one.
		
		@rtype: Transformer
		@return: next Transformer in chain or None
		'''
		return self._anotherTransformer
	def setAnotherTransformer(self, trans):
		'''
		Set the next transfomer in the chain.  The next transformer
		will be called *after* this one.
		
		@type	trans: Transformer
		@param	trans: Transformer to set
		'''
		self._anotherTransformer = trans
		return self
	
	def realEncode(self, data):
		'''
		Override this to implement your transform.
		
		@type	data: string
		@param	data: Data to transform
		@rtype: string
		@return: transformed data
		'''
		raise Exception("Error: realEncode(): Transformer does not work both ways")

	def realDecode(self, data):
		'''
		Override this to implement your transform.
		
		@type	data: string
		@param	data: Data to transform
		@rtype: string
		@return: transformed data
		'''
		raise Exception("Error: realDecode(): Transformer does not work both ways")


# end
