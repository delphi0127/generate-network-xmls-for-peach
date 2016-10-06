
'''
Mutators that operate on numerical types.

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

import sys, os, time, random, hashlib
from Peach.Generators.data import *
from Peach.mutator import *
from Peach.Engine.common import *

class NumericalVarianceMutator(Mutator):
	'''
	Produce numbers that are defaultValue - N to defaultValue + N.
	'''
	
	def __init__(self, peach, node):
		Mutator.__init__(self)
		#: Weight to be chosen randomly
		NumericalVarianceMutator.weight = 2
		
		self.name = "NumericalVarianceMutator"
		
		#: Is mutator finite?
		self.isFinite = True
		self._count = None
		
		self._dataElementName = node.getFullname()
		
		self._n = self._getN(node, 50)
		self._values = range(0 - self._n, self._n)
		self._currentCount = 0
		
		if isinstance(node, String):
			self._minValue = -2147483647
			self._maxValue = 4294967295
		else:
			self._minValue = node.getMinValue()
			self._maxValue = node.getMaxValue()
	
	def _getN(self, node, n):
		for c in node.hints:
			if c.name == 'NumericalVarianceMutator-N':
				try:
					n = int(c.value)
				except:
					raise PeachException("Expected numerical value for Hint named [%s]" % c.name)
		
		return n
	
	def next(self):
		self._currentCount += 1
		if self._currentCount >= len(self._values):
			raise MutatorCompleted()
	
	def getCount(self):
		return len(self._values)
	
	def supportedDataElement(e):
		
		if isinstance(e, String) and e.isMutable:
			# Look for NumericalString
			for hint in e.hints:
				if hint.name == "NumericalString":
					return True
		
		# Disable for 8 bit ints, we try all values already
		if (isinstance(e, Number) or isinstance(e, Flag)) and e.isMutable and e.size > 8:
			return True
		
		return False
	supportedDataElement = staticmethod(supportedDataElement)
	
	def sequencialMutation(self, node):
		
		self.changedName = node.getFullnameInDataModel()

		# If a negative value is passed into struct.pack
		# we end up generating 0 for that value.  instead
		# lets verify the generated value against min/max
		# and skip bad values.
		while True:
			# Sometimes self._n == 0, catch that here
			if self._currentCount >= len(self._values):
				return
			
			node.currentValue = long(node.getInternalValue()) - self._values[self._currentCount]
			
			# Is number okay?
			if node.currentValue >= self._minValue and node.currentValue <= self._maxValue:
				break
			
			# If not lets skip to next iteration
			try:
				self.next()
				
			except:
				break
		
		if isinstance(node, String):
			node.currentValue = unicode(node.currentValue)
	
	def randomMutation(self, node, rand):
		self.changedName = node.getFullnameInDataModel()
		try:
			count = rand.choice(self._values)
			node.currentValue = str(long(node.getInternalValue()) + count)
			if isinstance(node, String):
				node.currentValue = unicode(node.currentValue)
		except ValueError:
			# Okay to skip, another mutator probably
			# changes this value already (like a datatree one)
			pass


class NumericalEdgeCaseMutator(Mutator):
	'''
	This is a straight up generation class.  Produces values
	that have nothing todo with defaultValue :)
	'''
	
	_values = None
	_allowedSizes = [8, 16, 24, 32, 64]
	
	def __init__(self, peach, node):
		Mutator.__init__(self)
		#: Weight to be chosen randomly
		NumericalEdgeCaseMutator.weight = 3
		
		#: Is mutator finite?
		self.isFinite = True
		self.name = "NumericalEdgeCaseMutator"
		self._peach = peach
		self._count = None
		
		self._n = self._getN(node, 50)
		
		if self._values == None:
			self._populateValues()
		
		if isinstance(node, String):
			self._size = 32
		else:
			self._size = node.size
		
		# For flags, pick the next proper size up
		if self._size not in self._allowedSizes:
			for s in self._allowedSizes:
				if self._size <= s:
					self._size = s
					break
		
		self._dataElementName = node.getFullname()
		self._currentCount = 0
		
		if isinstance(node, String):
			self._minValue = -2147483647
			self._maxValue = 4294967295
		else:
			self._minValue = node.getMinValue()
			self._maxValue = node.getMaxValue()

	def _populateValues(self):
		NumericalEdgeCaseMutator._values = {}
		
		nums = []
		try:
			gen = BadNumbers8()
			while True:
				nums.append(int(gen.getValue()))
				gen.next()
		except:
			pass
		
		self._values[8] = nums
		
		nums = []
		try:
			
			gen = BadNumbers16(None, self._n)
			while True:
				nums.append(int(gen.getValue()))
				gen.next()
		except:
			pass
		
		self._values[16] = nums
		
		nums = []
		try:
			gen = BadNumbers24(None, self._n)
			while True:
				nums.append(int(gen.getValue()))
				gen.next()
		except:
			pass
		
		self._values[24] = nums
		
		nums = []
		try:
			gen = BadNumbers32(None, self._n)
			while True:
				nums.append(int(gen.getValue()))
				gen.next()
		except:
			pass
		
		self._values[32] = nums
		
		nums = []
		try:
			gen = BadNumbers(None, self._n)
			while True:
				nums.append(int(gen.getValue()))
				gen.next()
		except:
			pass
	
		self._values[64] = nums
	
	def next(self):
		self._currentCount += 1
		if self._currentCount >= len(self._values[self._size]):
			raise MutatorCompleted()
	
	def getCount(self):
		
		if self._count == None:
			cnt = 0
			for i in self._values[self._size]:
				if i < self._minValue or i > self._maxValue:
					continue
				
				cnt += 1
			
			self._count = cnt
		
		return self._count

	def supportedDataElement(e):
		
		if isinstance(e, String) and e.isMutable:
			# Look for NumericalString
			for hint in e.hints:
				if hint.name == "NumericalString":
					return True
		
		if (isinstance(e, Number) or isinstance(e, Flag)) and e.isMutable:
			return True
		
		return False
	supportedDataElement = staticmethod(supportedDataElement)

	def _getN(self, node, n):
		for c in node.hints:
			if c.name == 'NumericalEdgeCaseMutator-N':
				try:
					n = int(c.value)
				except:
					raise PeachException("Expected numerical value for Hint named [%s]" % c.name)
		
		return n

	def sequencialMutation(self, node):
		self.changedName = node.getFullnameInDataModel()
		# If a negative value is passed into struct.pack
		# we end up generating 0 for that value.  instead
		# lets verify the generated value against min/max
		# and skip bad values.
		while True:
			if isinstance(node, String):
				node.currentValue = unicode(self._values[self._size][self._currentCount])
			else:
				node.currentValue = self._values[self._size][self._currentCount]
			
			# Is number okay?
			if long(node.currentValue) >= self._minValue and long(node.currentValue) <= self._maxValue:
				break
			
			# If not lets skip to next iteration
			try:
				self.next()
				
			except:
				break
	
	def randomMutation(self, node, rand):
		self.changedName = node.getFullnameInDataModel()
		if isinstance(node, String):
			node.currentValue = unicode(rand.choice(self._values[self._size]))
		else:
			node.currentValue = rand.choice(self._values[self._size])


#class NumericalEvenDistributionMutator(Mutator):
#	'''
#	This mutator will generate numbers evenly distributed through
#	the total numerical space of the number range.
#	'''
#	
#	_values = None
#	
#	def __init__(self, peach, node):
#		Mutator.__init__(self)
#		#: Weight to be chosen randomly
#		self.weight = 3
#		
#		#: Is mutator finite?
#		self.isFinite = True
#		self.name = "NumericalEdgeCaseMutator"
#		self._peach = peach
#		
#		self._n = self._getN(node, 50)
#		
#		if self._values == None:
#			self._populateValues()
#		
#		if isinstance(node, String):
#			self._size = 32
#		else:
#			self._size = node.size
#		
#		self._dataElementName = node.getFullname()
#		self._random = random.Random()
#		self._currentCount = 0
#		
#		if isinstance(node, String):
#			self._minValue = 0
#			self._maxValue = 4294967295
#		else:
#			self._minValue = node.getMinValue()
#			self._maxValue = node.getMaxValue()
#
#	def _populateValues(self):
#		NumericalEdgeCaseMutator._values = {}
#		
#		nums = []
#		try:
#			gen = BadNumbers8()
#			while True:
#				nums.append(int(gen.getValue()))
#				gen.next()
#		except:
#			pass
#		
#		self._values[8] = nums
#		
#		nums = []
#		try:
#			
#			gen = BadNumbers16(None, self._n)
#			while True:
#				nums.append(int(gen.getValue()))
#				gen.next()
#		except:
#			pass
#		
#		self._values[16] = nums
#		
#		nums = []
#		try:
#			gen = BadNumbers24(None, self._n)
#			while True:
#				nums.append(int(gen.getValue()))
#				gen.next()
#		except:
#			pass
#		
#		self._values[24] = nums
#		
#		nums = []
#		try:
#			gen = BadNumbers32(None, self._n)
#			while True:
#				nums.append(int(gen.getValue()))
#				gen.next()
#		except:
#			pass
#		
#		self._values[32] = nums
#		
#		nums = []
#		try:
#			gen = BadNumbers(None, self._n)
#			while True:
#				nums.append(int(gen.getValue()))
#				gen.next()
#		except:
#			pass
#	
#		self._values[64] = nums
#	
#	def next(self):
#		self._currentCount += 1
#		if self._currentCount >= len(self._values[self._size]):
#			raise MutatorCompleted()
#	
#	def getCount(self):
#		return len(self._values[self._size])
#
#	def supportedDataElement(e):
#		
#		if isinstance(e, String):
#			# Look for NumericalString
#			for hint in e.hints:
#				if hint.name == "NumericalString":
#					return True
#		
#		if isinstance(e, Number) and e.isMutable:
#			return True
#		
#		return False
#	supportedDataElement = staticmethod(supportedDataElement)
#
#	def _getN(self, node, n):
#		for c in node.hints:
#			if c.name == 'NumericalEdgeCaseMutator-N':
#				try:
#					n = int(c.value)
#				except:
#					raise PeachException("Expected numerical value for Hint named [%s]" % c.name)
#		
#		return n
#
#	def sequencialMutation(self, node):
#		if isinstance(node, String):
#			node.currentValue = unicode(self._values[self._size][self._currentCount])
#		else:
#			node.currentValue = self._values[self._size][self._currentCount]
#	
#	def randomMutation(self, node):
#		if isinstance(node, String):
#			node.currentValue = unicode(self._random.choice(self._values[self._size]))
#		else:
#			node.currentValue = self._random.choice(self._values[self._size])
#


class FiniteRandomNumbersMutator(Mutator):
	'''
	Produce a finite number of random numbers for
	each <Number> element.
	'''
	
	def __init__(self, peach, node):
		Mutator.__init__(self)
		#: Weight to be chosen randomly
		FiniteRandomNumbersMutator.weight = 2
		
		self.name = "FiniteRandomNumbersMutator"
		self._peach = peach
		self._countThread = None
		
		self._n = self._getN(node, 5000)
		self._currentCount = 0
		
		if isinstance(node, String):
			self._minValue = 0
			self._maxValue = 4294967295
		else:
			self._minValue = node.getMinValue()
			self._maxValue = node.getMaxValue()
	
	def next(self):
		self._currentCount += 1
		if self._currentCount > self._n:
			raise MutatorCompleted()
	
	def getCount(self):
		return self._n
	
	def supportedDataElement(e):
		
		if (isinstance(e, Number) or isinstance(e, Flag)) and e.isMutable and e.size > 8:
			return True
		
		if isinstance(e, String) and e.isMutable:
			for hint in e.hints:
				if hint.name == "NumericalString":
					return True
		
		return False
	supportedDataElement = staticmethod(supportedDataElement)
	
	def _getN(self, node, n):
		for c in node.hints:
			if c.name == 'FiniteRandomNumbersMutator-N':
				try:
					n = int(c.value)
				except:
					raise PeachException("Expected numerical value for Hint named [%s]" % c.name)
		
		return n
	
	def sequencialMutation(self, node):
		
		# Allow us to skip ahead and always get same number
		rand = random.Random()
		rand.seed(hashlib.sha512(str(self._currentCount)).digest())
		
		self.changedName = node.getFullnameInDataModel()
		if isinstance(node, String):
			node.currentValue = unicode(rand.randint(self._minValue, self._maxValue))
		else:
			node.currentValue = rand.randint(self._minValue, self._maxValue)
	
	def randomMutation(self, node, rand):
		self.changedName = node.getFullnameInDataModel()
		if isinstance(node, String):
			node.currentValue = unicode(rand.randint(self._minValue, self._maxValue))
		else:
			node.currentValue = rand.randint(self._minValue, self._maxValue)



# end
