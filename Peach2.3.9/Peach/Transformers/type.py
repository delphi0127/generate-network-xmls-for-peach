
'''
Type transforms (atoi, itoa, etc).
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

# $Id: type.py 2475 2011-07-08 12:21:47Z meddingt $

import  struct,types, sys
from types import *
from Peach.transformer import Transformer

class Pack(Transformer):
	'''Simple pack transform.  Only a single piece of data can be used.
	Usefull to generate binary data from a generator.
	
	Format   	C Type   	Python   	Notes 
	x 	pad byte 	no value 	 
	c 	char 	string of length 1 	 
	b 	signed char 	integer 	 
	B 	unsigned char 	integer 	 
	h 	short 	integer 	 
	H 	unsigned short 	integer 	 
	i 	int 	integer 	 
	I 	unsigned int 	long 	 
	l 	long 	integer 	 
	L 	unsigned long 	long 	 
	q 	long long 	long 	(1)
	Q 	unsigned long long 	long 	(1)
	f 	float 	float 	 
	d 	double 	float 	 
	s 	char[] 	string 	 
	p 	char[] 	string 	 
	P 	void * 	integer 	 
	'''
	
	def __init__(self, packFormat):
		'''Create a Pack trasnformer.  packFormat is a standard pack
		format string.  Format string should only contain a single
		data place holder.'''
		Transformer.__init__(self)
		self._packFormat = packFormat
	
	def realEncode(self, data):
		'''Run pack on data'''
		
		return struct.pack(self._packFormat, data)


class NumberToString(Transformer):
	'''Transforms any type of number (int, long, float) to string.'''
	
	def __init__(self, formatString = None):
		'''Create NumberToString Instance.  formatString is a standard 
		Python string formater (optional).'''
		Transformer.__init__(self)
		self._formatString = formatString
	
	def realEncode(self, data):
		'''Convert number to string.  If no formatString was specified
		in class contructor data type is dynamicly determined and converted
		using a default formatString of "%d", "%f", or "%d" for Int, Float,
		and Long respectively.'''
		
		if self._formatString == None:
			retType = type(data)
			if retType is IntType:
				return "%d" % data
			elif retType is FloatType:
				return "%f" % data
			elif retType is LongType:
				return "%d" % data
			else:
				return data
		
		return self._formatString % data


class StringToInt(Transformer):
	'''Transform a string into an integer (atoi).'''
	def realEncode(self, data):
		return long(data)


class StringToFloat(Transformer):
	'''Transform a string into an float (atof).'''
	def realEncode(self, data):
		return float(data)


class IntToHex(Transformer):
	'''Transform an integer into hex.'''
	
	def __init__(self, withPrefix = 0):
		'''Create IntToHex object.  withPrefix flag indicates if
		0x prefix should be tagged onto string.  Default is no.'''
		Transformer.__init__(self)
		self._withPrefix = withPrefix
	
	def realEncode(self, data):
		
		if type(data) == StringType:
			data = long(data)
		
		ret = hex(data)
		if self._withPrefix == 0:
			return ret[2:]
		
		return ret

class _AsNumber(Transformer):
	'''Transform an number to a specific size 'n stuff'''
	
	def __init__(self, isSigned = 1, isLittleEndian = 1):
		'''
		@type	isSigned: number
		@param	isSigned: 1 for signed, 0 for unsigned
		@type	isLittleEndian: number
		@param	isLittleEndian: 1 for signed, 0 for unsigned
		'''
		
		Transformer.__init__(self)
		self._isSigned = isSigned
		self._isLittleEndian = isLittleEndian
	
	def _unfuglyNumber(self, data):
		'''
		Will attempt to figure out if the incoming data
		is a byte stream that must be converted to get our
		number we will then cast.  Due to StaticBinary issues.
		
		Chears to Blake for pointing this out.
		'''
		
		try:
			# First check to see if we need todo this
			if long(data) == long(str(data)):
				return long(data)
		except:
			pass
		
		#print "_unfuglyNumber(%s)" % repr(data), data
		
		# Now lets unfugly the thing
		hexString = ""
		for c in data:
			h = hex(ord(c))[2:]
			if len(h) < 2:
				h = "0" + h
			
			hexString += h
		
		return long(hexString, 16)
	
	def realEncode(self, data):
		
		data = self._unfuglyNumber(data)
		
		packStr = ''
		
		if self._isLittleEndian == 1:
			packStr = '<'
		else:
			packStr = '>'
		
		if self._isSigned == 1:
			packStr += self._packFormat.lower()
		else:
			packStr += self._packFormat.upper()
			
		# Prevent silly deprication warnings from Python
		if packStr[1] == 'b' and data > 0xfe:
			data = 0
		elif packStr[1] == 'B' and (data > 0xff or data < 0):
			data = 0
		elif packStr[1] == 'h' and data > 0xfffe:
			data = 0
		elif packStr[1] == 'H' and (data > 0xffff or data < 0):
			data = 0
		elif packStr[1] == 'i' and data > 0xfffffffe:
			data = 0
		elif packStr[1] == 'L' and (data > 0xffffffff or data < 0):
			data = 0
		elif packStr[1] == 'q' and data > 0xfffffffffffffffe:
			data = 0
		elif packStr[1] == 'Q' and (data > 0xffffffffffffffff or data < 0):
			data = 0
		
		try:
			return struct.pack(packStr, long(data))
		
		except:
			return struct.pack(packStr, 0)
		
	def realDecode(self, data):
		
		packStr = ''
		
		if self._isLittleEndian == 1:
			packStr = '<'
		else:
			packStr = '>'
		
		if self._isSigned == 1:
			packStr += self._packFormat.lower()
		else:
			packStr += self._packFormat.upper()
		
		try:
			return struct.unpack(packStr, data)[0]
		except:
			return 0


class AsInt8(_AsNumber):
	'''Transform an number to an INT8 or UINT8
	'''
	_packFormat = 'b'
	
class AsInt16(_AsNumber):
	'''Transform an number to an INT16 or UINT16
	'''
	_packFormat = 'h'

class AsInt24(Transformer):
	'''Transform an number to a UINT24 (don't ask)
	'''
	
	def __init__(self, isSigned = 1, isLittleEndian = 1):
		'''
		@type	isSigned: number
		@param	isSigned: 1 for signed, 0 for unsigned (we ignore this)
		@type	isLittleEndian: number
		@param	isLittleEndian: 1 for signed, 0 for unsigned
		'''
		
		Transformer.__init__(self)
		self._isLittleEndian = isLittleEndian
	
	def realEncode(self, data):
		
		try:
			data = long(data)
			packStr = ''
		
			if self._isLittleEndian == 1:
				packStr = '<'
			else:
				packStr = '>'
		
			packStr += 'L'
			v = struct.pack(packStr, data)
			
			if self._isLittleEndian == 1:
				return v[:3]
			else:
				return v[1:]
		except:
			return '0'
		
class AsInt32(_AsNumber):
	'''Transform an number to an INT32 or UINT32
	'''
	_packFormat = 'l'

class AsInt64(_AsNumber):
	'''Transform an number to an INT64 or UINT64
	'''
	_packFormat = 'q'


class UnsignedNumberToString(Transformer):
	'''
	Transforms unsigned numbers to strings
	'''
	
	def __init__(self):
		Transformer.__init__(self)
		self._size = None
	
	def realEncode(self, data):
		self._size = size = len(data) * 8
		
		if size == 0:
			return ""
		elif size == 8:
			return str(struct.unpack("B", data)[0])
		elif size == 16:
			return str(struct.unpack("H", data)[0])
		elif size == 24:
			raise Exception("24 bit numbers not supported")
		elif size == 32:
			return str(struct.unpack("I", data)[0])
		elif size == 64:
			return str(struct.unpack("Q", data)[0])
		
		raise Exception("Unknown numerical size:")
	
	def realDecode(self, data):
		size = self._size
		
		if size == None:
			return ""
		
		if size == 8:
			return struct.pack("B", data)
		elif size == 16:
			return struct.pack("H", data)
		elif size == 24:
			raise Exception("24 bit numbers not supported")
		elif size == 32:
			return struct.pack("I", data)
		elif size == 64:
			return struct.pack("Q", data)
		
		raise Exception("Unknown numerical size")


class SignedNumberToString(Transformer):
	'''
	Transforms unsigned numbers to strings
	'''
	
	def __init__(self):
		Transformer.__init__(self)
		self._size = None
	
	def realEncode(self, data):
		self._size = size = len(data) * 8
		
		if size == 0:
			return ""
		elif size == 8:
			return str(struct.unpack("b", data)[0])
		elif size == 16:
			return str(struct.unpack("h", data)[0])
		elif size == 24:
			raise Exception("24 bit numbers not supported")
		elif size == 32:
			return str(struct.unpack("i", data)[0])
		elif size == 64:
			return str(struct.unpack("q", data)[0])
		
		raise Exception("Unknown numerical size")
	
	def realDecode(self, data):
		size = self._size
		
		if size == None:
			return ""
		
		if size == 8:
			return struct.pack("b", data)
		elif size == 16:
			return struct.pack("h", data)
		elif size == 24:
			raise Exception("24 bit numbers not supported")
		elif size == 32:
			return struct.pack("i", data)
		elif size == 64:
			return struct.pack("q", data)
		
		raise Exception("Unknown numerical size")




# end
