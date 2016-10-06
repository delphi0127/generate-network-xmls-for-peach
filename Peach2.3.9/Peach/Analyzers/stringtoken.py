'''
Analyzers that produce data models from Strings

@author: Michael Eddington
@version: $Id$
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
#   Adam Cecchetti (adam@cecchetti.com)

# $Id$

from Peach.Engine.dom import *
from Peach.Engine.common import *
from Peach.analyzer import *

class StringTokenAnalyzer(Analyzer):
	'''
	Produces a tree of strings based on token precidence
	'''
	
	#: Does analyzer support asDataElement()
	supportDataElement = True
	#: Does analyzer support asCommandLine()
	supportCommandLine = False
	#: Does analyzer support asTopLevel()
	supportTopLevel = True
	
	def asDataElement(self, parent, args, data):
		'''
		Called when Analyzer is used in a data model.
		
		Should return a DataElement such as Block, Number or String.
		'''
		
		if not isinstance(parent, String):
			raise PeachException("Error, StringTokenAnalyzer can only be attached to String data elements.")
		
		#data = unicode(data, 'latin-1')
		
		self.stringType = parent.type
		dom = self._tokenizeString(data, None)
		
		# Handle null termination
		if parent.nullTerminated:
			blob = Blob(None, None)
			
			if parent.type == 'wchar':
				blob.defaultValue = "\x00"
			else:
				blob.defaultValue = "\x00\x00"
			
			dom.append(blob)
		
		# Replace parent with new dom
		
		parentOfParent = parent.parent
		dom.name = parent.name
		
		indx = parentOfParent.index(parent)
		del parentOfParent[parent.name]
		parentOfParent.insert(indx, dom)
		
		# now just cross our fingers :)
	
	def asCommandLine(self, args):
		'''
		Called when Analyzer is used from command line.  Analyzer
		should produce Peach PIT XML as output.
		'''
		raise Exception("asCommandLine not supported")
	
	def asTopLevel(self, peach, args):
		'''
		Called when Analyzer is used from top level.
		
		From the top level producing zero or more data models and
		state models is possible.
		'''
		self.stringType = parent.type
		dom = DataModel()
		dom.append(self._tokenizeString)
		
		return dom

	def _buildString(self, buff, parent = None):
		
		s = String(None, parent)
		s.type = self.stringType
		s.defaultValue = buff
		
		try:
			i = long(node.defaultValue)
			
			hint = Hint("NumericalString", s)
			hint.value = "true"
			s.hints.append(hint)
		except:
			pass
		
		return s

	def _tokenizeString(self, string, tokens = None):
		
		if string == None:
			return None
		
		if tokens == None:
			# Tokens in order of precidence
			tokens = [u'\0', u'\n', u'\r', u'<', u'>', u'?', u';',u',', u'|', u'@', u':', u'(', u')',
					  u'{', u'}', u'[', u']', u'/', u'\\', u'&', u'=', u' ', u'-', u'+', u'.']
		
		# Tokens that group parts of a string
		pairs = [
			[u'{', u'}'],
			[u'(', u')'],
			[u'[', u']'],
			[u'<', u'>'],
			]
		
		topNode = Block(None, None)
		topNode.append(self._buildString(string))
		
		for p in pairs:
			self._pairTree(p, topNode)
		
		for t in tokens:
			self._tokenTree(t, topNode)
		
		return topNode

	def _pairTree(self, p, node):
		
		if isinstance(node, Block):
			for c in node:
				self._pairTree(p, c)
			
			return
		
		string = node.defaultValue
		
		index1 = string.find(p[0])
		if index1 == -1:
			return
		
		index2 = string[index1:].find(p[1])
		if index2 == -1:
			return
		index2 += index1
		
		block = Block(None, None)
		
		pre = string[:index1]
		tokStart = string[index1]
		middle = string[index1+1:index2]
		tokEnd = string[index2]
		after = string[index2+1:]
		
		if len(pre) > 0:
			block.append(self._buildString(pre))
		
		block.append(self._buildString(tokStart))
		block.append(self._buildString(middle))
		block.append(self._buildString(tokEnd))
		
		if len(after) > 0:
			block.append(self._buildString(after))
		
		block.name = node.name
		node.parent[node.name] = block

	def _split(self, string, tok):
		'''
		A version of split that also returns the tokens.
		'''
		
		pos = string.find(tok)
		lastPos = 0
		parts = []
		
		if pos == -1:
			return parts
		
		while pos > -1:
			parts.append(string[:pos])
			parts.append(string[pos:pos+1])
			string = string[pos+1:]
			lastPos = pos
			pos = string.find(tok)
		
		parts.append(string)
		
		return parts
	
	def _tokenTree(self, token, node):
		
		if isinstance(node, Block):
			for c in node:
				self._tokenTree(token, c)
			
			return
		
		if len(node.defaultValue) < 2:
			return
		
		stuff = self._split(node.defaultValue, token)
		
		if len(stuff) == 0:
			return
		
		block = Block(node.name, None)
		
		for s in stuff:
			block.append(self._buildString(s))
		
		node.parent[node.name] = block
	
# end
