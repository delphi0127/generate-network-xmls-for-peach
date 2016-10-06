
'''
Mutator base classes and interfaces.

A Mutator implements a method of mutating data/state for a Peach 2
fuzzer.  For example a mutator might change the state flow defined
by a Peach fuzzer.  Another mutator might mutate data based on
known relationships.  Another mutator might perform numerical type
tests against fields.

@author: Michael Eddington
@version: $Id: mutator.py 2243 2010-12-09 21:33:27Z meddingt $
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

# $Id: mutator.py 2243 2010-12-09 21:33:27Z meddingt $

import random, threading, random, hashlib
import pickle, types
from Peach.Engine.dom import *

class Mutator(object):
	'''
	A Mutator implements a method of mutating data/state for a Peach 2
	fuzzer.  For example a mutator might change the state flow defined
	by a Peach fuzzer.  Another mutator might mutate data based on
	known relationships.  Another mutator might perform numerical type
	tests against fields.
	'''
	
	elementType = "mutator"
	dataTypes = ['template', 'string', 'number', 'flags', 'choice', 'sequence', 'blob', 'block']
	_random = random.Random()
	#: Weight to be chosen randomly
	weight = 1
	
	def __init__(self):
		self.name = "Mutator"
		self._count = None
		self.changedName = "N/A"
		
		#: Is mutator finite?
		self.isFinite = False
	
	def supportedDataElement(self, node):
		'''
		Returns true if element is supported by
		this mutator
		'''
		
		if isinstance(e, DataElement) and e.isMutable:
			return True
		
		return False
	supportedDataElement = staticmethod(supportedDataElement)
	
	def next(self):
		'''
		Goto next mutation.  When this is called
		the state machine is updated as needed.
		'''
		pass
	
	def getCount(self):
		'''
		If mutator is finite than the total test count
		can be calculated.  This calculation cannot
		occur until after the state machine has been run
		the first time.  Once the state machine has been
		run the count can be calculated.  This typically
		occurs in a separate thread as it can take some
		time to calculate.
		
		This method will return None until a the correct
		value has been calculated.
		'''
		return self._count
	
	def sequencialMutation(self, node):
		'''
		Perform a sequencial mutation
		'''
		pass
	
	def randomMutation(self, node):
		'''
		Perform a random mutation
		'''
		pass
	
#class MutatorCollection:
#	'''
#	Aggrigated collection of mutators.
#	'''
#	
#	def __init__(self, mutators):
#		self.name = "MutatorCollection"
#		
#		# Have we cycled all finite mutators yet?
#		self._cycledAll = False
#		# Current finite cycle position
#		self._cyclePos = 0
#		
#		self._mutators = mutators
#		self._finiteMutators = []
#		self._infiniteMutators = []
#		self._mutator = None
#		
#		self._masterCount = 0
#		self._stateMasterCount = -1
#		
#		for m in self._mutators:
#			if m.isFinite():
#				self._finiteMutators.append(m)
#			else:
#				self._infiniteMutators.append(m)
#		
#		# Current finite potition
#		self._curFinite = 0
#		self._maxFinite = len(self._finiteMutators)
#		self._maxInfinite = len(self._infiniteMutators)
#		
#		if self._maxFinite > 0:
#			self._mutator = self._finiteMutators[0]
#		
#		elif self._maxInfinite > 0:
#			self._cycledAll = True
#			self._mutator = self._getRandomInfiniteMutator()
#		
#		else:
#			raise Exception("MutatorCollection: No mutators!")
#	
#	def currentMutator(self):
#		return self._mutator
#	
#	def isFinite(self):
#		'''
#		Some mutators could contine forever, this
#		should indicate.
#		'''
#		
#		return len(self._infiniteMutators) == 0
#	
#	def reset(self):
#		'''
#		Reset mutator
#		'''
#		
#		self._cycledAll = False
#		self._cyclePos = 0
#		self._curFinite = 0
#		
#		for m in self._mutators:
#			m.reset()
#		
#		if self._maxFinite > 0:
#			self._mutator = self._finiteMutators[0]
#		
#		elif self._maxInfinite > 0:
#			self._cycledAll = True
#			self._mutator = self._getRandomInfiniteMutator()
#	
#	def next(self):
#		'''
#		Goto next mutation.  When this is called
#		the state machine is updated as needed.
#		'''
#		try:
#			# Increment current mutator
#			self._mutator.next()
#			
#			# If we have not cycled through all finite mutators
#			# lets do that first.  This is to make sure they can
#			# all start calculating there total tests for us.
#			#
#			# Note: In the case of no finite mutators we have
#			# already set self._cycledAll to True up in the
#			# constructor and also reset()
#			if not self._cycledAll:
#				self._cyclePos += 1
#				
#				if self._cyclePos >= self._maxFinite:
#					self._cycledAll = True
#					self._mutator = self._finiteMutators[self._curFinite]
#				
#				else:
#					self._mutator = self._finiteMutators[self._cyclePos]
#			
#			# Otherwise do the normal stuff
#			else:
#				
#				# If we are out of finite mutators grab a random
#				# infinte mutator.
#				if self._curFinite >= self._maxFinite:
#					self._mutator = self._getRandomInfiniteMutator()
#		
#		except MutatorCompleted:
#			
#			# If we have not cycled through all finite mutators
#			# lets do that first.  This is to make sure they can
#			# all start calculating there total tests for us.
#			#
#			# Note: In the case of no finite mutators we have
#			# already set self._cycledAll to True up in the
#			# constructor and also reset()
#			#
#			# We sometimes end up here if the mutator only perfomrs
#			# a single round.  This will happen for things like the
#			# Null mutator or mutators that find nothing to operate
#			# on like the XmlW3CMutator which keys of <Hint>'s
#			if not self._cycledAll:
#				
#				self._cyclePos += 1
#				if self._cyclePos >= self._maxFinite:
#					self._cycledAll = True
#					self._mutator = self._finiteMutators[self._curFinite]
#				
#				else:
#					self._mutator = self._finiteMutators[self._cyclePos]
#			
#			# Otherwise we will do the normal crazy stuff that we do :)
#			else:
#				
#				# Goto next finite mutator
#				self._curFinite += 1
#				
#				# See if we are are really done
#				if self._curFinite >= self._maxFinite and self._maxInfinite == 0:
#					raise MutatorCompleted()
#				
#				# Grab a random infinite mutator
#				elif self._curFinite >= self._maxFinite:
#					self._mutator = self._getRandomInfiniteMutator()
#				
#				# Get the new finite mutator
#				else:
#					self._mutator = self._finiteMutators[self._curFinite]
#		
#		self._masterCount += 1
#	
#	def _getRandomInfiniteMutator(self):
#		'''
#		Get a random infinite mutator.
#		'''
#		
#		idx = random.randint(0, self._maxInfinite)
#		return self._infiniteMutators[idx]
#	
#	def getState(self):
#		'''
#		Return a binary string that contains
#		any information about current state of
#		Mutator.  This state information should be
#		enough to let the same mutator "restart"
#		and continue when setState() is called.
#		'''
#		
#		return str(self._masterCount - 2)
#	
#	def setState(self, statePickle):
#		'''
#		Set the state of this object.  Should put us
#		back in the same place as when we said
#		"getState()".
#		'''
#		self._stateMasterCount = int(statePickle)
#		try:
#			for i in xrange(self._masterCount, self._stateMasterCount):
#				self.next()
#		except:
#			pass
#	
#	def getCount(self, verbose = False):
#		'''
#		This count will change as we go through mutators.
#		'''
#		
#		if not self.isFinite():
#			return -1
#		
#		if not self._cycledAll:
#			return -1
#		
#		count = 0
#		for m in self._finiteMutators:
#			if m.getCount() > -1:
#				count += m.getCount()
#			else:
#				#print "%s not reporting" % m.name
#				return -1
#		
#		if verbose:
#			for m in self._finiteMutators:
#				cnt = m.getCount()
#				print "Mutator %s is reporting %d test cases" % (m.name, cnt)
#		
#		return count
#
#	#####################################################
#	# Callbacks when Action needs a value
#	
#	def getActionValue(self, action):
#		return self._mutator.getActionValue(action)
#	
#	def getActionParamValue(self, action):
#		return self._mutator.getActionParamValue(action)
#	
#	def getActionChangeStateValue(self, action, value):
#		return self._mutator.getActionParamValue(action, value)
#	
#	#####################################################
#	# Event callbacks for state machine
#	
#	def onStateStart(self, state):
#		return self._mutator.onStateStart(state)
#	
#	def onStateComplete(self, state):
#		return self._mutator.onStateComplete(state)
#	
#	def onActionStart(self, action):
#		return self._mutator.onActionStart(action)
#	
#	def onActionComplete(self, action):
#		return self._mutator.onActionComplete(action)
#	
#	def onStateMachineStart(self, stateMachine):
#		return self._mutator.onStateMachineStart(stateMachine)
#	
#	def onStateMachineComplete(self, stateMachine):
#		return self._mutator.onStateMachineComplete(stateMachine)
#
#class MutatorCountCalculator(threading.Thread):
#	'''
#	This class will try and calculate the total number
#	of test cases in another thread.
#	
#	When the result is available self.hasCountEvent will
#	be set.
#	'''
#	
#	def __init__(self, mutator):
#		threading.Thread.__init__(self)
#		self._mutator = mutator
#		self.hasCountEvent = threading.Event()
#		self.count = -1
#	
#	def run(self):
#		self.count = self._mutator.calculateCount()
#		self.hasCountEvent.set()
#
#class MutatorCollectionProxy(MutatorCollection):
#	'''
#	This class behaves like a proxy between
#	mutatorCollection and nullMutator(behaviorally)
#	
#	If a stateMachine is completely or partially non-mutatable(not being fuzzed at all) then
#	this class helps MutatorCollection to run properly ;)
#	'''
#	def __init__(self, mutators):
#		MutatorCollection.__init__(self, mutators)
#		self._isStateMachineStatic = False
#	
#	def onStateMachineStart(self, engine):
#		MutatorCollection.onStateMachineStart(self, engine)
#		self._isStateMachineStatic = self._isStatic(engine.stateMachine)
#		# OK state machine is started so advance to the first path if possible
#		# if engine.pathFinder.canMove():
#		#	engine.pathFinder.next()
#	
#	def onStateMachineComplete(self, engine):
#		MutatorCollection.onStateMachineComplete(self, engine)
#		#StateMachine is completed, reset pathFinder 
#		engine.pathFinder.reset()
#		
#	def next(self):
#		if self._isStateMachineStatic:
#			self._isStateMachineStatic = False
#			raise MutatorCompleted()
#		else:
#			MutatorCollection.next(self)
#			
#	'''
#	@note: this method was removed!
#	def getActionValue(self, action):
#		#print "ACTION: %s isStatic:%s" % (action.name, action.isStatic)
#		val = MutatorCollection.getActionValue(self, action)
#		if action.isStatic:
#			val =  action.template.value;
#		
#		return val
#	'''
#	
#	'''
#	Determine if an element isStatic or not
#	by recursively looking at its child elements
#	'''
#	def _isStatic(self, elem):
#		if not isinstance(elem, Mutatable):
#			return True
#		
#		ret = elem.isMutable == False
#		for child in elem:
#			if isinstance(child, Mutatable):
#				ret = ret and self._isStatic(child)
#	
#		return ret
		
class MutatorCompleted(Exception):
	'''
	At end of available mutations
	'''
	pass

class MutatorError(Exception):
	'''
	Bad stuff just occured!
	'''
	pass

# end
