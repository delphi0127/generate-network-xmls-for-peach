# -*- coding: utf8 -*-

'''
Several testcases around <String> and it's arguments.
'''

import unittest
import utils

def suite():
	suite = unittest.TestSuite()
	suite.addTest(IncomingString1TestCase())
	suite.addTest(StringTestCase())
	suite.addTest(StringNullTestCase())
	suite.addTest(StringPadTestCase())
	suite.addTest(StringPad2TestCase())
	suite.addTest(StringPad3TestCase())
	suite.addTest(StringPad4TestCase())
	suite.addTest(StringWideTestCase())
	suite.addTest(StringWide2TestCase())
	suite.addTest(StringLiteralTestCase())
	suite.addTest(StringArraysTestCase())
	
	return suite

class IncomingString1TestCase(utils.PeachSendAndRecvTestCase):
	
	def runTest(self):
		# Test
		self.peachUtils.SetSendAndReceiveData("Hello World!12345")
		self.peachUtils.RunPeachXml("strings1.xml")
		#self.peachUtils.RunDebugPeachXml("strings1.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == "Hello World!", 'strings1.xml failed, instead [%s]' % repr(ret)

class StringTestCase(utils.PeachTcpTestCase):
	
	def runTest(self):
		# Test
		self.peachUtils.RunPeachXml("strings.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == 'This is Hello World', 'strings.xml failed, instead [%s]' % repr(ret)
		
class StringNullTestCase(utils.PeachTcpTestCase):
	
	def runTest(self):
		# Test
		self.peachUtils.RunPeachXml("stringsNull.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == 'This is Hello World\0', 'stringsNull.xml failed, instead [%s]' % repr(ret)
		
class StringPadTestCase(utils.PeachTcpTestCase):
	
	def runTest(self):
		# Test
		self.peachUtils.RunPeachXml("stringsPad.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == '12345ZZZZZ', 'stringsPad.xml failed, instead [%s]' % repr(ret)
		
class StringPad2TestCase(utils.PeachTcpTestCase):
	
	def runTest(self):
		# Test
		self.peachUtils.RunPeachXml("stringsPad2.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == '12345\0\0\0\0\0', 'stringsPad2.xml failed, instead [%s]' % repr(ret)
		
class StringPad3TestCase(utils.PeachTcpTestCase):
	
	def runTest(self):
		# Test
		self.peachUtils.RunPeachXml("stringsPad3.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == '12345\xff\xff\xff\xff\xff', 'stringsPad3.xml failed, instead [%s]' % repr(ret)
		
class StringPad4TestCase(utils.PeachTcpTestCase):
	
	def runTest(self):
		# Test
		self.peachUtils.RunPeachXml("stringsPad4.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == '12345\'\'\'\'\'', 'stringsPad4.xml failed, instead [%s]' % repr(ret)
		
class StringWideTestCase(utils.PeachTcpTestCase):
	
	def runTest(self):
		# Test
		self.peachUtils.RunPeachXml("stringsWide.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == 'P\0E\0A\0C\0H\0', 'stringsWide.xml failed, instead [%s]' % repr(ret)
		
class StringWide2TestCase(utils.PeachTcpTestCase):
	
	def runTest(self):
		# Test
		self.peachUtils.RunPeachXml("stringsWide2.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == 'a\0b\0\0\0', 'stringsWide2.xml failed, instead [%s]' % repr(ret)
		
class StringLiteralTestCase(utils.PeachTcpTestCase):
	
	def runTest(self):
		# Test
		self.peachUtils.RunPeachXml("stringsLiteral.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == 'Peach', 'stringsLiteral.xml failed, instead [%s]' % repr(ret)
		
class StringArraysTestCase(utils.PeachTcpTestCase):
	
	def runTest(self):
		# Test
		self.peachUtils.RunPeachXml("stringsArrays.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == '1.0\n1.1\n1.2\n2.0\n2.1\n2.2\n3.0.1\n3.0.2\n3.1.1\n3.1.2\n3.2.1\n3.2.2\n4.0.1\n4.0.2\n4.1.1\n4.1.2\n4.2.1\n4.2.2\n', 'stringsArrays.xml failed, instead [%s]' % repr(ret)
		
class StringUtf8_1_TestCase(utils.PeachTcpTestCase):
	
	def runTest(self):
		# Test
		self.peachUtils.RunPeachXml("stringUtf8-1.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret.decode('utf8') == u"∞HelloHowAreYou", 'stringUtf8-1.xml failed, instead [%s]' % repr(ret)
		
		
if __name__ == "__main__":
    unittest.main()

# end
