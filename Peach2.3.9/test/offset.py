'''
Offset test cases
'''

import unittest
import utils

def suite():
	suite = unittest.TestSuite()
	suite.addTest(Offset1TestCase())
	suite.addTest(Offset2TestCase())
	suite.addTest(Offset3TestCase())
	suite.addTest(Offset4TestCase())
	suite.addTest(Offset5TestCase())
	suite.addTest(Offset6TestCase())
	return suite

class Offset1TestCase(utils.PeachTcpTestCase):
	
	def runTest(self):
		# Test
		self.peachUtils.RunPeachXml("offset1.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == '\x16\x10\n\x04PEACH4PEACH3PEACH2PEACH1', 'offset1.xml failed, instead [%s]' % repr(ret)

class Offset2TestCase(utils.PeachTcpTestCase):
	
	def runTest(self):
		# Test
		self.peachUtils.RunPeachXml("offset2.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == '28  28  80  92  93  93  103 CRAZY STRING!aslkjalskdjasaslkdjalskdjasdkjasdlkjasdALSKJDALKSJD11293812093aslkdjalskdjas', 'offset2.xml failed, instead [%s]' % repr(ret)

class Offset3TestCase(utils.PeachTcpTestCase):
	
	def runTest(self):
		# Test
		self.peachUtils.RunPeachXml("offset3.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == '24  24  37  41  58  65  CRAZY STRING!X\x02\x00\x00aslkdjalskdjasdlaFoo Me!\x00', 'offset3.xml failed, instead [%s]' % repr(ret)

class Offset4TestCase(utils.PeachTcpTestCase):
	
	def runTest(self):
		# Test
		self.peachUtils.RunPeachXml("offset4.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == 'CRAZY STRING!aslkjalskdjasaslkdjalskdjasdkjasdlkjasdALSKJDALKSJD11293812093aslkdjalskdjas0   0   52  64  65  65  75  ', 'offset4.xml failed, instead [%s]' % repr(ret)

class Offset5TestCase(utils.PeachTcpTestCase):
	
	def runTest(self):
		# Test
		self.peachUtils.RunPeachXml("offset5.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == '24  24  37  41  58  45  CRAZY STRING!X\x02\x00\x00aslkdjalskdjasdlaFoo Me!\x00', 'offset5.xml failed, instead [%s]' % repr(ret)

class Offset6TestCase(utils.PeachTcpTestCase):
	
	def runTest(self):
		# Test
		self.peachUtils.RunPeachXml("offset6.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == '24  24  37  41  58  45  CRAZY STRING!X\x02\x00\x00aslkdjalskdjasdlaFoo Me!\x00', 'offset6.xml failed, instead [%s]' % repr(ret)


if __name__ == "__main__":
    unittest.main()

# end
