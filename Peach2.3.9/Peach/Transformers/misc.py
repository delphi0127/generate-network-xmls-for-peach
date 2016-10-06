
'''
Misc transformers (eval, etc).
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

# $Id: misc.py 2020 2010-04-14 23:13:14Z meddingt $

import type, struct, sys
from Peach.transformer import Transformer
from Peach import transformer

#__all__ = ['Eval']

class Eval(Transformer):
	'''
	Eval a statement.  Utility transformer for when all else fails.
	'''
	
	_eval = None
	
	def __init__(self, eval, anotherTransformer = None):
		'''
		Eval a statement.  Should include a formater (%s) for data.
		'''
		transformer.Transformer.__init__(self, anotherTransformer)
		self._eval = eval
	
	def realEncode(self, data):
		return eval(self._eval % data)
	

# end
