'''
Several testcases around incoming data parsed into data map.
'''

import unittest
import utils
from struct import pack, unpack

def suite():
	suite = unittest.TestSuite()
	suite.addTest(IncomingNumber1TestCase())
	suite.addTest(IncomingHttp1TestCase())
	suite.addTest(IncomingSize1TestCase())
	suite.addTest(IncomingSize2TestCase())
	suite.addTest(IncomingSize3TestCase())
	suite.addTest(IncomingSize4TestCase())
	suite.addTest(IncomingSize5TestCase())
	suite.addTest(IncomingString1TestCase())
	suite.addTest(IncomingString2TestCase())
	suite.addTest(IncomingString3TestCase())
	suite.addTest(IncomingString4TestCase())
	#suite.addTest(IncomingString5TestCase())
	suite.addTest(IncomingBlob1TestCase())
	suite.addTest(IncomingBlob2TestCase())
	#suite.addTest(IncomingArray1TestCase())
	suite.addTest(IncomingArray2TestCase())
	suite.addTest(IncomingArray3TestCase())
	suite.addTest(IncomingWhen1ATestCase())
	suite.addTest(IncomingWhen1BTestCase())
	suite.addTest(IncomingWhen2ATestCase())
	suite.addTest(IncomingWhen2BTestCase())
	
	return suite

### TODO: Make this work.  Advanced case
#class IncomingArray1TestCase(utils.PeachSendAndRecvTestCase):
#	
#	def runTest(self):
#		# Test
#		self.peachUtils.SetSendAndReceiveData("1234567890ABCDE")
#		self.peachUtils.RunPeachXml("incomingArray1.xml")
#		ret = self.peachUtils.GetListenerData()
#		assert ret == "ABCDE", 'incomingArray1.xml failed, instead [%s]' % repr(ret)

class IncomingArray2TestCase(utils.PeachSendAndRecvTestCase):
	
	def runTest(self):
		# Test
		self.peachUtils.SetSendAndReceiveData("1234567890ABCDE")
		self.peachUtils.RunPeachXml("incomingArray2.xml")
		#self.peachUtils.RunDebugPeachXml("incomingArray2.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == "ABCDE", 'incomingArray2.xml failed, instead [%s]' % repr(ret)

class IncomingArray3TestCase(utils.PeachSendAndRecvTestCase):
	
	def runTest(self):
		# Test
		self.peachUtils.SetSendAndReceiveData("123412341234AA")
		self.peachUtils.RunPeachXml("incomingArray3.xml")
		#self.peachUtils.RunDebugPeachXml("incomingArray3.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == "123412341234AAAA", 'incomingArray3.xml failed, instead [%s]' % repr(ret)

class IncomingPngTestCase(utils.PeachSendAndRecvTestCase):
	
	def runTest(self):
		# Test
		fd = open("incomingPng.bin", "rb+")
		data = fd.read()
		fd.close()
		
		self.peachUtils.SetSendAndReceiveData(data)
		self.peachUtils.RunPeachXml("incomingPng.xml")
		#self.peachUtils.RunDebugPeachXml("incomingPng.xml")
		ret = self.peachUtils.GetListenerData()
		if ret != data:
			fd = open("out1.bin", "wb+")
			fd.write(ret)
			fd.close()
		assert ret == data, 'incomingPng.xml failed. %d, %d' % (len(ret), len(data))

class IncomingNumber1TestCase(utils.PeachSendAndRecvTestCase):
	
	def runTest(self):
		# Test
		self.peachUtils.SetSendAndReceiveData(pack('<b', 100))
		self.peachUtils.RunPeachXml("incomingNumber1.xml")
		#self.peachUtils.RunDebugPeachXml("incomingNumber1.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == pack('<b', 100), 'incomingNumber1.xml failed, instead [%s]' % repr(ret)

class IncomingSize1TestCase(utils.PeachSendAndRecvTestCase):
	
	def runTest(self):
		# Test
		self.peachUtils.SetSendAndReceiveData(pack('<b', 100) + 'A'*100)
		self.peachUtils.RunPeachXml("incomingSize1.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == pack('<b', 100) + 'A'*100, 'incomingSize1.xml failed, instead [%s]' % repr(ret)

class IncomingSize2TestCase(utils.PeachSendAndRecvTestCase):
	
	def runTest(self):
		# Test
		value = pack('<h', 100) + '12345' + 'A'*95
		self.peachUtils.SetSendAndReceiveData(value)
		self.peachUtils.RunPeachXml("incomingSize2.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == 'A'*95, 'incomingSize2.xml failed, instead [%s]' % repr(ret)

class IncomingSize3TestCase(utils.PeachSendAndRecvTestCase):
	
	def runTest(self):
		# Test
		value = pack('<h', 100) + 'A'*95 + '12345'
		self.peachUtils.SetSendAndReceiveData(value)
		self.peachUtils.RunPeachXml("incomingSize3.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == '12345', 'incomingSize3.xml failed, instead [%s]' % repr(ret)

class IncomingSize4TestCase(utils.PeachSendAndRecvTestCase):
	
	def runTest(self):
		# Test
		value = pack('<h', 100) + 'A'*100
		self.peachUtils.SetSendAndReceiveData(value)
		self.peachUtils.RunPeachXml("incomingSize4.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == 'A'*100, 'incomingSize4.xml failed, instead [%s]' % repr(ret)

class IncomingSize5TestCase(utils.PeachSendAndRecvTestCase):
	
	def runTest(self):
		# Test
		value = pack('<h', 100) + 'A'*100 + 'B'*10
		self.peachUtils.SetSendAndReceiveData(value)
		#self.peachUtils.RunDebugPeachXml("incomingSize5.xml")
		self.peachUtils.RunPeachXml("incomingSize5.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == 'B'*10, 'incomingSize5.xml failed, instead [%s]' % repr(ret)

class IncomingHttp1TestCase(utils.PeachSendAndRecvTestCase):
	def runTest(self):
		self.peachUtils.SetSendAndReceiveData("""HTTP/1.1 302 Object moved\r\nServer: Microsoft-IIS/5.1\r\nDate: Fri, 07 Mar 2008 04:54:39 GMT\r\nX-Powered-By: ASP.NET\r\nLocation: localstart.asp\r\nConnection: Keep-Alive\r\nContent-Length: 121\r\nContent-Type: text/html\r\nSet-Cookie: ASPSESSIONIDSSBDSTTR=MCOHEFGAADAHPPHEDFKLMEFH; path=/\r\nCache-control: private\r\n\r\n<head><title>Object moved</title></head>\r\n<body><h1>Object Moved</h1>This object may be found <a HREF="">here</a>.</body>""")
		self.peachUtils.RunPeachXml("incomingHttp1.xml")
		#self.peachUtils.RunDebugPeachXml("incomingHttp1.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == 'GET / HTTP/1.0\r\n\r\n', 'incomingHttp1.xml failed, instead got [%s]' % repr(ret)

class IncomingString1TestCase(utils.PeachSendAndRecvTestCase):
	
	def runTest(self):
		# Test
		value = '1234567890'
		self.peachUtils.SetSendAndReceiveData(value)
		self.peachUtils.RunPeachXml("incomingString1.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == value, 'incomingString1.xml failed, instead [%s]' % repr(ret)

class IncomingString2TestCase(utils.PeachSendAndRecvTestCase):
	
	def runTest(self):
		# Test
		value = '1234567890'
		self.peachUtils.SetSendAndReceiveData(value)
		self.peachUtils.RunPeachXml("incomingString2.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == value, 'incomingString2.xml failed, instead [%s]' % repr(ret)

class IncomingString3TestCase(utils.PeachSendAndRecvTestCase):
	
	def runTest(self):
		# Test
		value = '123456789\0'
		self.peachUtils.SetSendAndReceiveData(value)
		self.peachUtils.RunPeachXml("incomingString3.xml")
		#self.peachUtils.RunDebugPeachXml("incomingString3.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == value[:-1], 'incomingString3.xml failed, instead [%s]' % repr(ret)

class IncomingString4TestCase(utils.PeachSendAndRecvTestCase):
	
	def runTest(self):
		# Test
		value = '123456789\0'
		self.peachUtils.SetSendAndReceiveData(value)
		self.peachUtils.RunPeachXml("incomingString4.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == value, 'incomingString4.xml failed, instead [%s]' % repr(ret)

### TODO: Support this test case
#class IncomingString5TestCase(utils.PeachSendAndRecvTestCase):
#	
#	def runTest(self):
#		# Test
#		value = '\01\02\03\04\05\06\07\08\09\0\0'
#		self.peachUtils.SetSendAndReceiveData(value)
#		self.peachUtils.RunPeachXml("incomingString5.xml")
#		ret = self.peachUtils.GetListenerData()
#		assert ret == value, 'incomingString5.xml failed, instead [%s]' % repr(ret)
#

class IncomingBlob1TestCase(utils.PeachSendAndRecvTestCase):
	
	def runTest(self):
		# Test
		value = '1234567890'
		self.peachUtils.SetSendAndReceiveData(value)
		self.peachUtils.RunPeachXml("incomingBlob1.xml")
		#self.peachUtils.RunDebugPeachXml("incomingBlob1.xml")
		
		ret = self.peachUtils.GetListenerData()
		assert ret == value, 'incomingBlob1.xml failed, instead [%s]' % repr(ret)

class IncomingBlob2TestCase(utils.PeachSendAndRecvTestCase):
	
	def runTest(self):
		# Test
		value = '1234567890'
		self.peachUtils.SetSendAndReceiveData(value)
		self.peachUtils.RunPeachXml("incomingBlob2.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == value, 'incomingBlob2.xml failed, instead [%s]' % repr(ret)

class IncomingWhen1ATestCase(utils.PeachSendAndRecvTestCase):
	
	def runTest(self):
		# Test
		value = 'A12345'
		self.peachUtils.SetSendAndReceiveData(value)
		self.peachUtils.RunPeachXml("incomingWhen1.xml")
		#self.peachUtils.RunDebugPeachXml("incomingWhen1.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == value[1:], 'incomingWhen1.xml failed, instead [%s]' % repr(ret)

class IncomingWhen1BTestCase(utils.PeachSendAndRecvTestCase):
	
	def runTest(self):
		# Test
		value = 'B1234567890'
		self.peachUtils.SetSendAndReceiveData(value)
		self.peachUtils.RunPeachXml("incomingWhen1.xml")
		#self.peachUtils.RunDebugPeachXml("incomingWhen1.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == value[1:], 'incomingWhen1.xml failed, instead [%s]' % repr(ret)

class IncomingWhen2ATestCase(utils.PeachSendAndRecvTestCase):
	
	def runTest(self):
		# Test
		value = 'A12345'
		self.peachUtils.SetSendAndReceiveData(value)
		self.peachUtils.RunPeachXml("incomingWhen2.xml")
		#self.peachUtils.RunDebugPeachXml("incomingWhen2.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == value[1:], 'incomingWhen2.xml failed, instead [%s]' % repr(ret)

class IncomingWhen2BTestCase(utils.PeachSendAndRecvTestCase):
	
	def runTest(self):
		# Test
		value = 'B1234567890'
		self.peachUtils.SetSendAndReceiveData(value)
		self.peachUtils.RunPeachXml("incomingWhen2.xml")
		#self.peachUtils.RunDebugPeachXml("incomingWhen2.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == value[1:], 'incomingWhen2.xml failed, instead [%s]' % repr(ret)


if __name__ == "__main__":
    unittest.main()

# end
