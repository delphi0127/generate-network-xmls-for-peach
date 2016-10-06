'''
Analyzers convert data or specifications into models, both data and state.
The default analyzer is peach pit XML analyzer.

Analyzers can be applied inside of the DOM as well.

  <Analyzer class="">
    <Param name="" value="" />	<!-- Optional -->
  </Analyzer>

Analyzers for default implementation:

 * Peach PIT XML
 * String  Tokenizer
 * XML
 * WireShark
 
Other wanted analyzers:

 * Binary
 * RPC
 * DCOM
 * WebServices
 * HTTP POST/GET??

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

class Analyzer(object):
	'''
	Analyzers produce data and state models.  Examples of analyzers would be
	the parsing of Peach PIT XML files, tokenizing a string, building a data
	model based on XML file, etc.
	'''
	
	#: Default parser analyzer to use
	DefaultParser = None
	
	#: Does analyzer support asParser()
	supportParser = False
	#: Does analyzer support asDataElement()
	supportDataElement = False
	#: Does analyzer support asCommandLine()
	supportCommandLine = False
	#: Does analyzer support asTopLevel()
	supportTopLevel = False
	
	def __init__(self):
		pass

	def asParser(self, uri):
		'''
		Called when Analyzer is used as default PIT parser.
		
		Should produce a Peach DOM.
		'''
		raise Exception("Error, this analyzer cannot be used the parser.")

	def asDataElement(self, parent, args, dataBuffer):
		'''
		Called when Analyzer is used in a data model.
		
		Should return a DataElement such as Block, Number or String.
		'''
		raise PeachException("Error, this analyzer does not support being attached to a data element via the analyzer attribute.")
	
	def asCommandLine(self, args):
		'''
		Called when Analyzer is used from command line.  Analyzer
		should produce Peach PIT XML as output.
		'''
		raise PeachException("Error, this analyzer does not support running from the command line.")
	
	def asTopLevel(self, peach, args):
		'''
		Called when Analyzer is used from top level.
		
		From the top level producing zero or more data models and
		state models is possible.
		
		@type	args	Dictionary
		@param	args	Arguments from <Param>'s
		'''
		raise Exception("Error, this analyzer does not support being used as a top level element.")
	

# end
