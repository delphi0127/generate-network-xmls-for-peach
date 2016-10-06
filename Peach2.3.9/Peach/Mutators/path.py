
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

import sys, os, time, hashlib
from Peach.mutator import *
from Peach.mutatestrategies import *

class NullMutator(Mutator):
	'''
	Does not make any changes to data tree.  This is
	usually the first mutator applied to a fuzzing run
	so the generated data can be verified.
	'''
	
	def __init__(self, peach):
		Mutator.__init__(self)
		self.name = "NullMutator"
		
	def isFinite(self):
		'''
		Some mutators could contine forever, this
		should indicate.
		'''
		return True
	
	def next(self):
		'''
		Goto next mutation.  When this is called
		the state machine is updated as needed.
		'''
		
		raise MutatorCompleted()
	
	def getState(self):
		'''
		Return a binary string that contains
		any information about current state of
		Mutator.  This state information should be
		enough to let the same mutator "restart"
		and continue when setState() is called.
		'''
		
		return ''
	
	def setState(self, state):
		'''
		Set the state of this object.  Should put us
		back in the same place as when we said
		"getState()".
		'''
		pass
		
	def getCount(self):
		return 1

	#####################################################
	# Callbacks when Action needs a value
	
	def getActionValue(self, action):
		if action.template.modelHasOffsetRelation:
			stringBuffer = StreamBuffer()
			action.template.getValue(stringBuffer)
			stringBuffer.setValue("")
			stringBuffer.seekFromStart(0)
			action.template.getValue(stringBuffer)
			return stringBuffer.getValue()
		
		return action.template.getValue()
	
	def getActionParamValue(self, action):
		if action.template.modelHasOffsetRelation:
			stringBuffer = StreamBuffer()
			action.template.getValue(stringBuffer)
			stringBuffer.setValue("")
			stringBuffer.seekFromStart(0)
			action.template.getValue(stringBuffer)
			return stringBuffer.getValue()
		
		return action.template.getValue()
	
	def getActionChangeStateValue(self, action, value):
		return value
	

class PathValidationMutator(NullMutator, MutationStrategy):
	'''
	This mutator is just used to trace path
	of each test for path validation purposes
	so this is not an actual Mutator
	that is used on fuzzing
	'''
	
	def __init__(self):
		Mutator.__init__(self)
		self.states = []
		self.name = "PathValidationMutator"
		
	def onStateStarting(self, stateMachine, state):
		self.states.append(state.name)
		
	def onStateMachineStarting(self, engine):
		pass
		
	def onStateMachineComplete(self, engine):
		engine.pathFinder.reset()