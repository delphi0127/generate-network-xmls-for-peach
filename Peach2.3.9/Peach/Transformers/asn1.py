
'''
ASN.1 transformers.  These transformers perform correct ASN.1 encoding.  The
data Generators module contains a couple of additional ASN.1 classes
that perform incorrect encodings.

@author: Michael Eddington
@version: $Id: asn1.py 823 2008-04-06 20:59:41Z meddingt $
'''

#
# Copyright (c) 2007-2008 Michael Eddington
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

# $Id: asn1.py 823 2008-04-06 20:59:41Z meddingt $

try:
	from struct import *
	from Peach.transformer import Transformer
	from pyasn1.type import univ
	from pyasn1.codec import der, ber, cer
	
	class DerEncodeOctetString(Transformer):
		'''
		DER encode an octect string ASN.1 style
		'''
		
		def realEncode(self, data):
			return der.encoder.encode(univ.OctetString(data))
	
	class DerEncodeBitString(Transformer):
		'''
		DER encode a bit string ASN.1 style
		'''
		
		def realEncode(self, data):
			return der.encoder.encode(univ.BitString(data))
	
	class DerEncodeInteger(Transformer):
		'''
		DER encode an integer ASN.1 style
		'''
		
		def realEncode(self, data):
			return der.encoder.encode(univ.Integer(int(data)))
	
	class DerEncodeBoolean(Transformer):
		'''
		DER encode a boolean ASN.1 style.  Expects 0 or 1.
		'''
		
		def realEncode(self, data):
			data = int(data)
			if data != 0 and data != 1:
				raise Exception("DerEncodeBoolean transformer expects 0 or 1")
			
			return der.encoder.encode(univ.Boolean(data))
	
	class DerEncodeObjectIdentifier(Transformer):
		'''
		DER encode an object identifierASN.1 style.
		'''
		
		def realEncode(self, data):
			return der.encoder.encode(univ.ObjectIdentifier(data))

	# #############################################################
	
	class BerEncodeOctetString(Transformer):
		'''
		BER encode a string ASN.1 style
		'''
		
		def realEncode(self, data):
			return ber.encoder.encode(univ.OctetString(data))
	
	class BerEncodeBitString(Transformer):
		'''
		BER encode a bit string ASN.1 style
		'''
		
		def realEncode(self, data):
			return ber.encoder.encode(univ.BitString(data))
	
	class BerEncodeInteger(Transformer):
		'''
		BER encode an integer ASN.1 style
		'''
		
		def realEncode(self, data):
			return ber.encoder.encode(univ.Integer(int(data)))
	
	class BerEncodeBoolean(Transformer):
		'''
		BER encode a boolean ASN.1 style.  Expects 0 or 1.
		'''
		
		def realEncode(self, data):
			data = int(data)
			if data != 0 and data != 1:
				raise Exception("BerEncodeBoolean transformer expects 0 or 1")
			
			return ber.encoder.encode(univ.Boolean(data))
	
	class BerEncodeObjectIdentifier(Transformer):
		'''
		BER encode an object identifierASN.1 style.
		'''
		
		def realEncode(self, data):
			return ber.encoder.encode(univ.ObjectIdentifier(data))
	
	# #############################################################
	
	class CerEncodeOctetString(Transformer):
		'''
		CER encode a string ASN.1 style
		'''
		
		def realEncode(self, data):
			return cer.encoder.encode(univ.OctetString(data))
	
	class CerEncodeBitString(Transformer):
		'''
		CER encode a bit string ASN.1 style
		'''
		
		def realEncode(self, data):
			return cer.encoder.encode(univ.BitString(data))
	
	class CerEncodeInteger(Transformer):
		'''
		CER encode an integer ASN.1 style
		'''
		
		def realEncode(self, data):
			return cer.encoder.encode(univ.Integer(int(data)))
	
	class CerEncodeBoolean(Transformer):
		'''
		CER encode a boolean ASN.1 style.  Expects 0 or 1.
		'''
		
		def realEncode(self, data):
			data = int(data)
			if data != 0 and data != 1:
				raise Exception("CerEncodeBoolean transformer expects 0 or 1")
			
			return cer.encoder.encode(univ.Boolean(data))
	
	class CerEncodeObjectIdentifier(Transformer):
		'''
		CER encode an object identifierASN.1 style.
		'''
		
		def realEncode(self, data):
			return cer.encoder.encode(univ.ObjectIdentifier(data))
	
except:
	pass


# end
