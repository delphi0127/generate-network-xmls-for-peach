
'''
Used to verify state path

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

# $Id$

import sys, os, time
from Peach.mutatestrategies import MutationStrategy

class PathValidationStrategy(MutationStrategy):
	'''
	Used by path unittests
	'''
	
	def __init__(self, args):
		'''
		@type	args: Dictionary
		@param	args: Arguments
		'''
		MutationStrategy.__init__(self, args)
		self.states = []
	
	def isFinite(self):
		'''
		Will this mutation strategy ever end?
		'''
		return True
	
	def getCount(self):
		'''
		Return the number of test cases
		'''
		return 1
	
	## Events
	
	def onStateMachineFinished(self, stateEngine):
		'''
		Called as we exit the state machine
		
		@type	stateEngine: StateEngine instance
		@param	stateEngine: StateEngine instance in use
		'''
		stateEngine.pathFinder.reset()
	
	def onStateStarting(self, stateEngine, state):
		'''
		Called as we enter a new state
		
		@type	stateEngine: StateEngine instance
		@param	stateEngine: StateEngine instance in use
		@type	state: State instance
		@param	state: Current state
		'''
		self.states.append(state.name)
	
# end
