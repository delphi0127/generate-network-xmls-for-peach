
'''
Mutators that operate on blob types.

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

import sys, os, time, struct, traceback, hashlib
from Peach.mutator import *
from Peach.Engine.common import *

class DWORDSliderMutator(Mutator):
	'''
	Slides a DWORD through the blob.
	
	@author Chris Clark
	'''
	
	def __init__(self, peach, node):
		Mutator.__init__(self)
		#: Weight to be chosen randomly
		DWORDSliderMutator.weight = 2
		
		self.isFinite = True
		
		self.name = "DWORDSliderMutator"
		self._peach = peach
		self._curPos = 0
		
		self._len = len(node.getInternalValue())
		self._position = 0		
		self._dword = 0xFFFFFFFF
		self._counts = 0
	
	def next(self):
		self._position += 1
		if self._position >= self._len:
			raise MutatorCompleted()
		
	def getCount(self):
		return self._len

	def supportedDataElement(e):
		if (isinstance(e, Blob) or isinstance(e, Template)) and e.isMutable:
			for child in e.hints:
				if child.name == 'DWORDSliderMutator' and child.value == 'off':
					return False
			
			return True
		
		return False
	supportedDataElement = staticmethod(supportedDataElement)
	
	def sequencialMutation(self, node):
		self.changedName = node.getFullnameInDataModel()
		self._performMutation(node, self._position)
	
	def randomMutation(self, node, rand):
		self.changedName = node.getFullnameInDataModel()
		count = rand.randint(0, self._len-1)
		self._performMutation(node, count)

	def _performMutation(self, node, position):
		
		data = node.getInternalValue()
		length = len(data)
		
		if position >= length:
			return
		
		inject = ''
		remaining = length - position
		
		if remaining == 1:
			inject = struct.pack('B', self._dword & 0x000000FF)
		
		elif remaining == 2:
			inject = struct.pack('H', self._dword & 0x0000FFFF) #ushort
		
		elif remaining == 3: 
			inject = struct.pack('B', (self._dword & 0x00FF0000) >> 16) + \
				struct.pack('>H', self._dword & 0xFFFF)
		
		else:
			inject = struct.pack('L', self._dword)
		
		node.currentValue = data[:position] + inject + data[position + len(inject):]


class BitFlipperMutator(Mutator):
	'''
	Flip a % of total bits in blob.  Default % is 20.
	'''
	
	def __init__(self, peach, node):
		Mutator.__init__(self)
		#: Weight to be chosen randomly
		BitFlipperMutator.weight = 3
		
		self.isFinite = True
		self.name = "BitFlipperMutator"
		self._peach = peach
		self._n = self._getN(node, None)
		self._current = 0
		self._len = len(node.getInternalValue())
		
		if self._n != None:
			self._count = self._n
		
		else:
			self._count = long((len(node.getInternalValue())*8) * 0.2)
	
	def _getN(self, node, n):
		for c in node.hints:
			if c.name == 'BitFlipperMutator-N':
				try:
					n = int(c.value)
				except:
					raise PeachException("Expected numerical value for Hint named [%s]" % c.name)
		
		return n
	
	def next(self):
		self._current += 1
		if self._current > self._count:
			raise MutatorCompleted()
	
	def getCount(self):
		return self._count
	
	def supportedDataElement(e):
		if (isinstance(e, Blob) or isinstance(e, Template)) and e.isMutable:
			return True
		
		return False
	supportedDataElement = staticmethod(supportedDataElement)
	
	def sequencialMutation(self, node):
		# Allow us to skip ahead and always get same number
		rand = random.Random()
		rand.seed(hashlib.sha512(str(self._current)).digest())
		
		self.changedName = node.getFullnameInDataModel()
		data = node.getInternalValue()
		
		for i in range(rand.randint(0, 10)):
			if self._len - 1 <= 0:
				count = 0
			else:
				count = rand.randint(0, self._len-1)
				
			data = self._performMutation(data, count, rand)
			
		node.currentValue = data
	
	def randomMutation(self, node, rand):
		self.changedName = node.getFullnameInDataModel()
		data = node.getInternalValue()
		
		for i in range(rand.randint(0, 10)):
			if self._len -1 <= 0:
				count = 0
			else:
				count = rand.randint(0, self._len-1)
			
			data = self._performMutation(data, count, rand)
		
		node.currentValue = data
	
	def _performMutation(self, data, position, rand):
		length = len(data)
		
		if len(data) == 0:
			return data
		
		# How many bytes to change
		size = rand.choice([1, 2, 4, 8])
		
		if (position+size) >= length:
			position = length - size
		if position < 0:
			position = 0
		if size > length:
			size = length
		
		for i in range(position, position+size):
			byte = struct.unpack('B', data[i])[0]
			byte ^= rand.randint(0, 255)
			
			packedup = struct.pack("B", byte)
			data = data[:i] + packedup + data[i+1:]
		
		return data


class BlobMutator(BitFlipperMutator):
	'''
	This mutator will do more types of changes
	than BitFlipperMutator currently can perform.  We
	will grow the Blob, shrink the blob, etc.
	'''
	
	def __init__(self, peach, node):
		BitFlipperMutator.__init__(self, peach, node)
		
		self.name = "BlobMutator"
	
	def sequencialMutation(self, node):
		# Allow us to skip ahead and always get same number
		rand = random.Random()
		rand.seed(hashlib.sha512(str(self._current)).digest())
		
		self.changedName = node.getFullnameInDataModel()
		node.currentValue = self._performMutation(node, rand)
	
	def randomMutation(self, node, rand):
		self.changedName = node.getFullnameInDataModel()
		node.currentValue = self._performMutation(node, rand)

	def getRange(self, size, rand):
		start = rand.randint(0, size)
		end = rand.randint(0, size)
		
		if start > end:
			return (end, start)
		
		return (start, end)

	def getPosition(self, rand, size, len = 0):
		pos = rand.randint(0, size - len)
		return pos

	def _performMutation(self, node, rand):
		
		data = node.getInternalValue()
		
		func = rand.choice([
			self.changeExpandBuffer,
			self.changeReduceBuffer,
			self.changeChangeRange,
			self.changeChangeRangeSpecial,
			self.changeNullRange,
			self.changeUnNullRange,
			])
		
		#print "BlobMutator:", func
		return func(data, rand)
	
	def changeExpandBuffer(self, data, rand):
		'''
		Expand the size of our buffer
		'''
		
		size = rand.randint(0, 255)
		pos = self.getPosition(rand, size)
		
		return data[:pos] + self.generateNewBytes(size, rand) + data[pos:]
	
	def changeReduceBuffer(self, data, rand):
		'''
		Reduce the size of our buffer
		'''
		(start, end) = self.getRange(len(data), rand)
		
		return data[:start] + data[end:]
	
	def changeChangeRange(self, data, rand):
		'''
		Change a sequence of bytes in our buffer
		'''
		(start, end) = self.getRange(len(data), rand)
		
		if end > (start+100):
			end = start+100
		
		for i in range(start, end):
			data = data[:i] + chr(rand.randint(0, 255)) + data[i+1:]
		
		return data
	
	def changeChangeRangeSpecial(self, data, rand):
		'''
		Change a sequence of bytes in our buffer
		to some special chars.
		'''
		special = ["\x00", "\x01", "\xfe", "\xff"]
		(start, end) = self.getRange(len(data), rand)
		
		if end > (start+100):
			end = start+100
		
		for i in range(start, end):
			data = data[:i-1] + rand.choice(special) + data[i:]
		return data

	def changeNullRange(self, data, rand):
		'''
		Change a range of bytes to null.
		'''
		(start, end) = self.getRange(len(data), rand)
		
		if end > (start+100):
			end = start+100
		
		for i in range(start, end):
			data = data[:i-1] + chr(0) + data[i:]
		
		return data
	
	def changeUnNullRange(self, data, rand):
		'''
		Change all zero's in a range to something else.
		'''
		(start, end) = self.getRange(len(data), rand)
		
		if end > (start+100):
			end = start+100
		
		for i in range(start, end):
			if ord(data[i]) == 0:
				data = data[:i-1] + chr(rand.randint(1, 255)) + data[i:]
		
		return data

	# ######################################
	
	def generateNewBytes(self, size, rand):
		'''
		Generate new bytes to inject into Blob.
		'''
		
		func = rand.choice([
			self.GenerateNewBytesSingleRandom,
			self.GenerateNewBytesIncrementing,
			self.GenerateNewBytesZero,
			self.GenerateNewBytesAllRandom,
			])
		
		return func(size, rand)
	
	def GenerateNewBytesSingleRandom(self, size, rand):
		'''
		Generate a buffer of size bytes, each
		byte is the same random number.
		'''
		
		return chr(rand.randint(0,255)) * size
	
	def GenerateNewBytesIncrementing(self, size, rand):
		'''
		Generate a buffer of size bytes, each
		byte is incrementing from a random start.
		'''
		
		buff = ""
		x = rand.randint(0, size)
		for i in range(0, size):
			
			if i+x > 255:
				return buff
			
			buff += chr(i+x)
		
		return buff
	
	def GenerateNewBytesZero(self, size, rand):
		'''
		Generate a buffer of size bytes, each
		byte is zero (NULL).
		'''
		return "\0" * size
	
	def GenerateNewBytesAllRandom(self, size, rand):
		'''
		Generate a buffer of size bytes, each
		byte is randomly generated.
		'''
		buff = ""
		
		for i in range(size):
			buff += chr(rand.randint(0, 255))
		
		return buff

if __name__ == '__main__':
	data = "skaldjalskjdlaskjdlaskjdlaksjdlaksjdlkajsdlkajsdljaslkdjalskdjalskdjalskjdlaksjdlakjsd"
	b = BlobMutator(None, None)
	b.changeExpandBuffer(data)
	b.changeReduceBuffer(data)
	b.changeChangeRange(data)
	b.changeChangeRangeSpecial(data)
	b.changeNullRange(data)
	b.changeUnNullRange(data)

# end
