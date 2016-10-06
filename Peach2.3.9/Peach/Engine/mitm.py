
'''
Peach-in-The-Middle Fuzzing

This module is the core of th PiTM support in Peach

@author: Michael Eddington
@version: $Id: mitm.py 780 2008-03-23 02:58:49Z meddingt $
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

# $Id: mitm.py 780 2008-03-23 02:58:49Z meddingt $

'''

DESIGN

Goal:  Make it easy to fuzz protocols that have complex state transitions.  And example would be RDP (remote desktop protocol).

FEATURES

OPERATION

1. Cause client to perform usecase
	a. Watch sequence of packets
	b. Build minimal StateMachine based on packet sequence
	
	-> Have collection of possible Templates.  Attempt to fit each template
	   to locate best fit.

2. Rest client & server

3. Loop the following:
	a. [C] Start usecase
	b. [P] Mutate usecase
	c. [A] Monitor server for fault
	d. Reset state

4. Move to next use case and GOTO #1

NEED

 - Client control
 - Server monitor (have)
 - MiTM part

'''

import sys, re, types
import traceback

import Ft.Xml.Domlette
from Ft.Xml.Domlette import Print, PrettyPrint

from Peach.Engine.dom import *
from Peach.Engine.parser import *
#from build import BuildPeach
from Peach.Engine.incoming import *

def Debug(level, msg):
	if level <= 1:
		print msg

def peachPrint(msg):
	print "peachPrint: ", msg


" [C] -> [PEACH] -> [S]"
"   Right         Left "
"   Ouput->    <-Input "
class PitmStateEngine:
	
	def __init__(self, engine, stateMachine, publisherRight, publisherLeft):
		self.engine = engine
		
		# Get and run initial state
		self.stateMachine = stateMachine
		self.publisherRight = publisherRight
		self.publisherLeft = publisherLeft
		self.f = peachPrint
	
	def run(self, mutator):
		'''
		Returns true if all test cases have been performed.
		'''
		Debug(1, "StateEngine.run: %s" % self.stateMachine.name)
		
		# listen on tcp socket A
		
		
		# connect out on tcp socket B
		
		
		while True:
			
			# read from A
			
			# write to B
			
			# read from B
			
			# write to A
			
			pass
		
		# close both sockets
		
		mutator.onStateStart(state)
		
		# EVENT: onEnter
		if state.onEnter != None:
			environment = {
				'peach' : self.engine.peach,
				'state' : state,
				'stateMachine' : state.parent,
				'peachPrint' : self.f,
				'mutator' : mutator
				}
			
			self._evalEvent(state.onEnter, environment)
		
		try:
			
			# Start with first action and continue along
			for action in state:
				if action.elementType != 'action':
					continue
				
				self._runAction(action, mutator)
			
			# EVENT: onExit
			if state.onExit != None:
				environment = {
					'peach' : self.engine.peach,
					'state' : state,
					'stateMachine' : state.parent,
					'peachPrint' : self.f,
					'mutator' : mutator
					}
				
				self._evalEvent(state.onExit, environment)
				
			mutator.onStateComplete(state)
			
		except StateChangeStateException, e:
			
			# EVENT: onExit
			if state.onExit != None:
				environment = {
					'peach' : self.engine.peach,
					'state' : state,
					'stateMachine' : state.parent,
					'peachPrint' : self.f,
					'mutator' : mutator
					}
				
				self._evalEvent(state.onExit, environment)
			
			mutator.onStateComplete(state)
			
			self._runState(e.state, mutator)
		

	def _evalEvent(self, code, environment):
		'''
		Eval python code returning result.
		
		code - String
		environment - Dictionary, keys are variables to place in local scope
		'''
		
		#print globals()
		scope = { '__builtins__' : globals()['__builtins__'] }
		for k in environment.keys():
			scope[k] = environment[k]
		
		ret = eval(code, scope, scope)
		
		return ret
	

	def _runAction(self, action, mutator):
		
		Debug(1, "StateEngine._runAction: %s" % action.name)
				
		mutator.onActionStart(action)
		
		# EVENT: when
		if action.when != None:
			environment = {
				'peach' : self.engine.peach,
				'action' : action,
				'state' : action.parent,
				'stateMachine' : action.parent.parent,
				'mutator' : mutator,
				'peachPrint' : self.f
				}
			
			#print action.parent.parent
			#for k in action.parent.parent._childrenHash.keys():
			#	print "Key: ", k
			
			if not self._evalEvent(action.when, environment):
				return
		
		# EVENT: onStart
		if action.onStart != None:
			environment = {
				'peach' : self.engine.peach,
				'action' : action,
				'state' : action.parent,
				'stateMachine' : action.parent.parent,
				'mutator' : mutator,
				'peachPrint' : self.f
				}
			
			self._evalEvent(action.onStart, environment)
		
		if action.type == 'input':
			"""
			Get input from left side
			
			1. Receive data from the left side
			2. Parse into template
			3. Pass back to right side
			"""
			
			action.value = None
			
			# Determine initial read size
			cracker = DataCracker(self.engine.peach)
			size = cracker.getInitialReadSize(action.template)
			Debug(1, "StateEngine._runAction(input): Found initial read size of %s" % size)
			
			data = ""
			dom = None
			
			# Parse input stream into template
			while True:
				try:
					print ">>STATE IS CALLING RECEIVE FOR %d BYTES" % size
					data += self.publisherLeft.receive(size)
					Debug(2, "======================================")
					cracker = DataCracker(self.engine.peach)
					dom = cracker.crackDataForTemplate(action.template, data)
					break
				
				except NeedMoreData, e:
					size = e.amount
					Debug(2, "Going back for: %d" % size)
					Debug(2, "Currently Have:")
					Debug(2, "><><><><><><><><><><><><><><><><><><")
					Debug(2, data)
					Debug(2, "><><><><><><><><><><><><><><><><><><")
			
			printDom(dom, 0)
			
			action.value = dom
			
			# Send data to right side
			self.publisherRight.send(action.value)
		
		elif action.type == 'output':
			"""
			Get ouput from right side
			
			1. Receive data from the right side
			2. Parse into template
			3. Pass back to left side
			"""
			
			action.value = None
			
			# Determine initial read size
			cracker = DataCracker(self.engine.peach)
			size = cracker.getInitialReadSize(action.template)
			Debug(1, "StateEngine._runAction(input): Found initial read size of %s" % size)
			
			data = ""
			dom = None
			
			# Parse input stream into template
			while True:
				try:
					print ">>STATE IS CALLING RECEIVE FOR %d BYTES" % size
					data += self.publisherRight.receive(size)
					Debug(2, "======================================")
					cracker = DataCracker(self.engine.peach)
					dom = cracker.crackDataForTemplate(action.template, data)
					break
				
				except NeedMoreData, e:
					size = e.amount
					Debug(2, "Going back for: %d" % size)
					Debug(2, "Currently Have:")
					Debug(2, "><><><><><><><><><><><><><><><><><><")
					Debug(2, data)
					Debug(2, "><><><><><><><><><><><><><><><><><><")
			
			printDom(dom, 0)
			
			action.value = dom
			action.value = mutator.getActionValue(action)
			
			self.publisherLeft.send(action.value)
		
		else:
			raise Exception("StateEngine._runAction(): Unknown action.type of [%s]" % str(action.type))
		
		# EVENT: onComplete
		if action.onComplete != None:
			environment = {
				'peach' : self.engine.peach,
				'action' : action,
				'state' : action.parent,
				'mutator' : mutator,
				'stateMachine' : action.parent.parent
				}
			
			self._evalEvent(action.onComplete, environment)
		
		mutator.onActionComplete(action)

class StateChangeStateException:
	def __init__(self, state):
		self.state = state
	
	def __str__(self):
		return "Exception: StateChangeStateException"

class StateError:
	def __init__(self, msg):
		self.msg = msg
	
	def __str__(self):
		return self.msg

# end
