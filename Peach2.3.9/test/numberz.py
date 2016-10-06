'''
Several testcases around <String> and it's arguments.
'''

import unittest
import utils
from struct import pack, unpack

def suite():
	suite = unittest.TestSuite()
	suite.addTest(NumberTestCase())
	suite.addTest(Number16TestCase())
	suite.addTest(Number32TestCase())
	suite.addTest(Number64TestCase())
	suite.addTest(NumberEndianBigTestCase())
	suite.addTest(NumberEndianBigUnsignedTestCase())
	suite.addTest(NumberEndianLittleTestCase())
	suite.addTest(NumberHexTestCase())
	suite.addTest(NumberLiteralTestCase())
	return suite

class NumberTestCase(utils.PeachTcpTestCase):
	
	def runTest(self):
		# Test
		self.peachUtils.RunPeachXml("numbers.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == pack('<b', 100), 'numbers.xml failed, instead [%s]' % repr(ret)

class Number16TestCase(utils.PeachTcpTestCase):
	
	def runTest(self):
		# Test
		self.peachUtils.RunPeachXml("numbers16.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == pack('<H', 0xffff), 'numbers16.xml failed, instead [%s]' % repr(ret)

class Number32TestCase(utils.PeachTcpTestCase):
	
	def runTest(self):
		# Test
		self.peachUtils.RunPeachXml("numbers32.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == pack('<i', 0xFFFFFE), 'numbers32.xml failed, instead [%s]' % repr(ret)

class Number64TestCase(utils.PeachTcpTestCase):
	
	def runTest(self):
		# Test
		self.peachUtils.RunPeachXml("numbers64.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == pack('<q', 0xfffffffe), 'numbers64.xml failed, instead [%s]' % repr(ret)

class NumberEndianBigTestCase(utils.PeachTcpTestCase):
	
	def runTest(self):
		# Test
		self.peachUtils.RunPeachXml("numbersEndianBig.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == pack('>h', 0xfffe), 'numbersEndianBig.xml failed, instead [%s]' % repr(ret)

class NumberEndianBigUnsignedTestCase(utils.PeachTcpTestCase):
	
	def runTest(self):
		# Test
		self.peachUtils.RunPeachXml("numbersEndianBigUnsigned.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == pack('>H', 0xfffe), 'numbersEndianBigUnsigned.xml failed, instead [%s]' % repr(ret)

class NumberEndianLittleTestCase(utils.PeachTcpTestCase):
	
	def runTest(self):
		# Test
		self.peachUtils.RunPeachXml("numbersEndianLittle.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == pack('<I', 0xFFFFFE), 'numbersEndianLittle.xml failed, instead [%s]' % repr(ret)

class NumberHexTestCase(utils.PeachTcpTestCase):
	
	def runTest(self):
		# Test
		self.peachUtils.RunPeachXml("numbersHex.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == pack('<B', 255), 'numbersHex.xml failed, instead [%s]' % repr(ret)

class NumberLiteralTestCase(utils.PeachTcpTestCase):
	
	def runTest(self):
		# Test
		self.peachUtils.RunPeachXml("numbersLiteral.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == pack('<B', 200), 'numbersLiteral.xml failed, instead [%s]' % repr(ret)


if __name__ == "__main__":
    unittest.main()

# end
