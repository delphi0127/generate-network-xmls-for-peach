
'''
A few standard fixups.
'''

#
# Copyright (c) 2008-2009 Michael Eddington
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
#
# $Id$

import operator
import zlib, hashlib, struct, binascii, array
from Peach.fixup import Fixup
from Peach.Engine.common import *
import Ft.Xml.Domlette
from Ft.Xml.Domlette import Print, PrettyPrint

class ExpressionFixup(Fixup):
	'''
	Sometimes you need to perform some math as the fixup.  This
	relation will take a ref, then an expression (python).
	'''
	
	def __init__(self, ref, expression):
		Fixup.__init__(self)
		self.ref = ref
		self.expression = expression
	
	def fixup(self):
		ref = self._findDataElementByName(self.ref)
		stuff = ref.getValue()
		if stuff == None:
			raise Exception("Error: ExpressionFixup was unable to locate [%s]" % self.ref)
		
		return evalEvent(self.expression, { "self" : self, "ref" : ref, "data" : stuff  }, ref)

class SHA224Fixup(Fixup):
	def __init__(self, ref):
		Fixup.__init__(self)
		self.ref = ref
			def fixup(self):
		self.context.defaultValue = "0"
		stuff = self._findDataElementByName(self.ref).getValue()
		if stuff == None:
			raise Exception("Error: SHA1Fixup was unable to locate [%s]" % self.ref)
		h = hashlib.sha224()
		h.update(stuff)
		return h.digest()
	
class SHA256Fixup(Fixup):
	def __init__(self, ref):
		Fixup.__init__(self)
		self.ref = ref
			def fixup(self):
		self.context.defaultValue = "0"
		stuff = self._findDataElementByName(self.ref).getValue()
		if stuff == None:
			raise Exception("Error: SHA256Fixup was unable to locate [%s]" % self.ref)
		h = hashlib.sha256()
		h.update(stuff)
		return h.digest()
	
class SHA384Fixup(Fixup):
	def __init__(self, ref):
		Fixup.__init__(self)
		self.ref = ref
			def fixup(self):
		self.context.defaultValue = "0"
		stuff = self._findDataElementByName(self.ref).getValue()
		if stuff == None:
			raise Exception("Error: SHA384Fixup was unable to locate [%s]" % self.ref)
		h = hashlib.sha384()
		h.update(stuff)
		return h.digest() 

class SHA512Fixup(Fixup):
	def __init__(self, ref):
		Fixup.__init__(self)
		self.ref = ref
		
	def fixup(self):
		self.context.defaultValue = "0"
		stuff = self._findDataElementByName(self.ref).getValue()
		if stuff == None:
			raise Exception("Error: SHA512Fixup was unable to locate [%s]" % self.ref)
		h = hashlib.sha512()
		h.update(stuff)
		return h.digest()
	class SHA1Fixup(Fixup):
	def __init__(self, ref):
		Fixup.__init__(self)
		self.ref = ref
		
	def fixup(self):
		self.context.defaultValue = "0"
		stuff = self._findDataElementByName(self.ref).getValue()
		if stuff == None:
			raise Exception("Error: SHA1Fixup was unable to locate [%s]" % self.ref)
		h = hashlib.sha1()
		h.update(stuff)
		return h.digest() 
	class MD5Fixup(Fixup):
	def __init__(self, ref):
		
		Fixup.__init__(self)
		self.ref = ref
			def fixup(self):
		self.context.defaultValue = "0"
		stuff = self._findDataElementByName(self.ref).getValue()
		if stuff == None:
			raise Exception("Error: MD5Fixup was unable to locate [%s]" % self.ref)
		h = hashlib.md5()
		h.update(stuff)
		return h.digest() 
	
class Crc32Fixup(Fixup):
	'''
	Standard CRC32 as defined by ISO 3309.  Used by PNG, zip, etc.
	'''
	
	def __init__(self, ref):
		Fixup.__init__(self)
		self.ref = ref
	
	def fixup(self):
		self.context.defaultValue = "0"
		stuff = self._findDataElementByName(self.ref).getValue()
		if stuff == None:
			raise Exception("Error: Crc32Fixup was unable to locate [%s]" % self.ref)
		
		crc = zlib.crc32(stuff)
		if crc < 0:
			crc = ~crc ^ 0xffffffff
		
		return crc

class LRCFixup(Fixup):
	
	def __init__(self, ref):
		Fixup.__init__(self)
		self.ref = ref
		
	def fixup(self):
		self.context.defaultValue = "0"
		stuff = self._findDataElementByName(self.ref).getValue()
		
		if stuff == None:
			raise Exception("Error: LRCFixup was unable to locate [%s]" % self.ref)
		
		lrc = 0
		for b in stuff:
			lrc ^= ord(b)
		return chr(lrc)

class Crc32DualFixup(Fixup):
	'''
	Standard CRC32 as defined by ISO 3309.  Used by PNG, zip, etc.
	'''
	
	def __init__(self, ref1, ref2):
		Fixup.__init__(self)
		self.ref1 = ref1
		self.ref2 = ref2
	
	def fixup(self):
		self.context.defaultValue = "0"
		stuff1 = self._findDataElementByName(self.ref1).getValue()
		stuff2 = self._findDataElementByName(self.ref2).getValue()
		if stuff1 == None or stuff2 == None:
			raise Exception("Error: Crc32DualFixup was unable to locate [%s] or [%s]" % (self.ref1, self.ref2))
		
		crc1 = zlib.crc32(stuff1)
		crc = zlib.crc32(stuff2, crc1)
		if crc < 0:
			crc = ~crc ^ 0xffffffff
		
		return crc


class EthernetChecksumFixup(Fixup):
	'''
	Ethernet Chucksum Fixup.
	'''
	
	def __init__(self, ref):
		Fixup.__init__(self)
		self.ref = ref
	
	def _checksum(self, checksum_packet):
		"""Calculate checksum"""
		ethernetKey = 0x04C11DB7
		return binascii.crc32(checksum_packet, ethernetKey)
	
	def fixup(self):
		self.context.defaultValue = "0"
		stuff = self._findDataElementByName(self.ref).getValue()
		if stuff == None:
			raise Exception("Error: EthernetChecksumFixup was unable to locate [%s]" % self.ref)
		
		return self._checksum(stuff)


class IcmpChecksumFixup(Fixup):
	'''
	Ethernet Chucksum Fixup.
	'''
	
	def __init__(self, ref):
		Fixup.__init__(self)
		self.ref = ref
	
	def _checksum(self, checksum_packet):
		"""Calculate checksum"""
		# add byte if not dividable by 2
		if len(checksum_packet) & 1:              
			checksum_packet = checksum_packet + '\0'
		# split into 16-bit word and insert into a binary array
		words = array.array('h', checksum_packet) 
		sum = 0
		
		# perform ones complement arithmetic on 16-bit words
		for word in words:
			sum += (word & 0xffff) 
		
		hi = sum >> 16 
		lo = sum & 0xffff 
		sum = hi + lo
		sum = sum + (sum >> 16)
		
		return (~sum) & 0xffff # return ones complement
	
	def fixup(self):
		self.context.defaultValue = "0"
		stuff = self._findDataElementByName(self.ref).getValue()
		if stuff == None:
			raise Exception("Error: IcmpChecksumFixup was unable to locate [%s]" % self.ref)
		
		return self._checksum(stuff)

# This Fixup only works on windows... wrap in a try
try:
	import sspi, sspicon
	
	class SspiAuthenticationFixup(Fixup):
		'''
		Perform basic SSPI authentication. Assumes a two step auth.
		'''
		
		_sspi = None
		_firstObj = None
		_secondObj = None
		_data = None
		
		def __init__(self, firstSend, secondSend, user = None, group = None, password = None):
			Fixup.__init__(self)
			self.firstSend = firstSend
			self.secondSend = secondSend
			self.username = user
			self.workgroup = group
			self.password = password
		
		def getXml(self):
			dict = {}
			doc  = Ft.Xml.Domlette.NonvalidatingReader.parseString("<Peach/>", "http://phed.org")
			self.context.getRoot().toXmlDom(doc.rootNode.firstChild, dict)
			return doc
		
		def fixup(self):
			try:
				fullName = self.context.getFullname()
				xml = self.getXml()
				
				firstFullName = str(xml.xpath(self.firstSend)[0].getAttributeNS(None, "fullName"))
				firstFullName = firstFullName[firstFullName.index('.')+1:]
				
				if fullName.find(firstFullName) > -1 and SspiAuthenticationFixup._firstObj != self.context:
					
					#scflags = sspicon.ISC_REQ_INTEGRITY|sspicon.ISC_REQ_SEQUENCE_DETECT|\
					#	sspicon.ISC_REQ_REPLAY_DETECT|sspicon.ISC_REQ_CONFIDENTIALITY
					scflags = sspicon.ISC_REQ_INTEGRITY|sspicon.ISC_REQ_SEQUENCE_DETECT|\
						sspicon.ISC_REQ_REPLAY_DETECT
					
					SspiAuthenticationFixup._firstObj = self.context
					SspiAuthenticationFixup._sspi = sspi.ClientAuth(
						"Negotiate",
						"",	# client_name
						(self.username, self.workgroup, self.password),	# auth_info
						None, # targetsn (target security context provider)
						scflags, #scflags	# None,	# security context flags
						)
					
					(done, data) = SspiAuthenticationFixup._sspi.authorize(None)
					data = data[0].Buffer
					SspiAuthenticationFixup._data = data
					
					return data
				
				if fullName.find(firstFullName) > -1:
					return SspiAuthenticationFixup._data
				
				secondFullName = str(xml.xpath(self.secondSend)[0].getAttributeNS(None, "fullName"))
				secondFullName = secondFullName[secondFullName.index('.')+1:]
				if fullName.find(secondFullName) > -1 and SspiAuthenticationFixup._secondObj != self.context:
					inputData = self.context.getInternalValue()
					
					if len(inputData) < 5:
						return None
					
					(done, data) = SspiAuthenticationFixup._sspi.authorize(inputData)
					
					data = data[0].Buffer
					
					SspiAuthenticationFixup._secondObj = self.context
					SspiAuthenticationFixup._data = data
					
					return data
				
				if fullName.find(secondFullName) > -1:
					return SspiAuthenticationFixup._data
				
			except:
				print "!!! EXCEPTION !!!"
				print repr(sys.exc_info())
				pass

except:
	pass

# end
