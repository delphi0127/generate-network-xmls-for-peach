'''
Mutation Strategies

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

# $Id$

import sys, os, time, random
from Peach.mutator import MutatorCompleted

class MutationStrategy(object):
	'''
	Mutation strategies control how fuzzing occurs, weather that be
	changing each field sequencially or randomly selecting 5 fields
	to change each test case.
	
	Mutation strategies are implemented by overriding event handlers
	and using them to affect the state machine, data models, etc.
	'''
	
	DefaultStrategy = None
	
	def __init__(self, node, parent):
		'''
		@type	args: Dictionary
		@param	args: Arguments
		'''
		self.parent = parent  # This will be a Test object
		pass
	
	def isFinite(self):
		'''
		Will this mutation strategy ever end?
		'''
		return True
	
	def getCount(self):
		'''
		Return the number of test cases
		'''
		return None

	def next(self):
		'''
		Goto next test sequence.
		
		Throws MutatorCompleted when we are done.
		'''
		raise MutatorCompleted()

	def currentMutator(self):
		'''
		Return the current Mutator in use
		'''
		pass
	
	## Events
	
	def onTestCaseStarting(self, test, count, stateEngine):
		'''
		Called as we start a test case
		
		@type	test: Test instance
		@param	test: Current test being run
		@type	count: int
		@param	count: Current test #
		@type	stateEngine: StateEngine instance
		@param	stateEngine: StateEngine instance in use
		'''
		pass
	
	def onTestCaseFinished(self, test, count, stateEngine):
		'''
		Called as we exit a test case
		
		@type	test: Test instance
		@param	test: Current test being run
		@type	count: int
		@param	count: Current test #
		@type	stateEngine: StateEngine instance
		@param	stateEngine: StateEngine instance in use
		'''
		pass
	
	def onFaultDetected(self, test, count, stateEngine, results, actionValues):
		'''
		Called if a fault was detected during our current
		test case.
		
		@type	test: Test instance
		@param	test: Current test being run
		@type	count: int
		@param	count: Current test #
		@type	stateEngine: StateEngine instance
		@param	stateEngine: StateEngine instance in use
		@type	results: Dictionry
		@param	results: Monitor results
		@type	actionValues: Dictionary
		@param	actionValues: Values used to perform test
		'''
		pass
	
	def onStateMachineStarting(self, stateEngine):
		'''
		Called as we enter the state machine
		
		@type	stateEngine: StateEngine instance
		@param	stateEngine: StateEngine instance in use
		'''
		pass
	
	def onStateMachineFinished(self, stateEngine):
		'''
		Called as we exit the state machine
		
		@type	stateEngine: StateEngine instance
		@param	stateEngine: StateEngine instance in use
		'''
		pass
	
	def onStateStarting(self, stateEngine, state):
		'''
		Called as we enter a new state
		
		@type	stateEngine: StateEngine instance
		@param	stateEngine: StateEngine instance in use
		@type	state: State instance
		@param	state: Current state
		'''
		pass	
	
	def onStateFinished(self, stateEngine, state):
		'''
		Called as we exit a state
		
		@type	stateEngine: StateEngine instance
		@param	stateEngine: StateEngine instance in use
		@type	state: State instance
		@param	state: Current state
		'''
		pass
	
	def onStateChange(self, currentState, newState):
		'''
		Called before state is changed.  If result
		if non-None we can select a different state
		to change to.
		
		@type	currentState: State instance
		@param	currentState: Current State
		@type	newState: State instance
		@param	newState: New state we are moving to
		@return Returns None or a different state instance
		'''
		return None
	
	def onActionStarting(self, state, action):
		'''
		Called as we enter an action
		
		@type	state: State
		@param	state: Current state
		@type	action: Action
		@param	action: Action we are starting
		'''
		pass
	
	def onActionFinished(self, state, action):
		'''
		Called as we exit an action
		
		@type	state: State
		@param	state: Current state
		@type	action: Action
		@param	action: Action we are starting
		'''
		pass
	
	def onDataModelGetValue(self, action, dataModel):
		'''
		Called before getting a value from a data model
		
		@type	action: Action
		@param	action: Action we are starting
		@type	dataModel: Template
		@param	dataModel: Data model we are using
		'''
		pass

# end
