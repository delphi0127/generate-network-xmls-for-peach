'''
Test for the Data element
'''

import unittest
import utils

def suite():
	suite = unittest.TestSuite()
	suite.addTest(Data1TestCase())
	suite.addTest(Data2TestCase())
	suite.addTest(Data3TestCase())
	suite.addTest(Data4TestCase())
	suite.addTest(Data5TestCase())
	suite.addTest(Data6TestCase())
	suite.addTest(Data7TestCase())
	suite.addTest(Data8TestCase())
	suite.addTest(DataFile1TestCase())
	suite.addTest(DataExpression1TestCase())
	return suite

class Data1TestCase(utils.PeachTcpTestCase):
	def runTest(self):
		self.peachUtils.RunPeachXml("data1.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == 'DataForPeach', 'data1.xml failed, instead got [%s]' % repr(ret)

class Data2TestCase(utils.PeachTcpTestCase):
	def runTest(self):
		self.peachUtils.RunPeachXml("data2.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == 'DataForPeach', 'data2.xml failed, instead got [%s]' % repr(ret)

class Data3TestCase(utils.PeachTcpTestCase):
	def runTest(self):
		self.peachUtils.RunPeachXml("data3.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == 'DataForPeach', 'data3.xml failed, instead got [%s]' % repr(ret)

class Data4TestCase(utils.PeachTcpTestCase):
	def runTest(self):
		self.peachUtils.RunPeachXml("data4.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == 'DataForPeach', 'data4.xml failed, instead got [%s]' % repr(ret)

class Data5TestCase(utils.PeachTcpTestCase):
	def runTest(self):
		self.peachUtils.RunPeachXml("data5.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == 'DataForPeach', 'data5.xml failed, instead got [%s]' % repr(ret)

class Data6TestCase(utils.PeachTcpTestCase):
	def runTest(self):
		self.peachUtils.RunPeachXml("data6.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == 'DataForPeach', 'data6.xml failed, instead got [%s]' % repr(ret)

class Data7TestCase(utils.PeachTcpTestCase):
	def runTest(self):
		self.peachUtils.RunPeachXml("data7.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == 'Return\nOther', 'data7.xml failed, instead got [%s]' % repr(ret)

class Data8TestCase(utils.PeachTcpTestCase):
	def runTest(self):
		self.peachUtils.RunPeachXml("data8.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == '\x03man\x06fuzzed\x02me\x00', 'data8.xml failed, instead got [%s]' % repr(ret)

class DataFile1TestCase(utils.PeachTcpTestCase):
	def runTest(self):
		self.peachUtils.RunPeachXml("dataFile1.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == 'Hello World!', 'dataFile1.xml failed, instead got [%s]' % repr(ret)

class DataExpression1TestCase(utils.PeachTcpTestCase):
	def runTest(self):
		self.peachUtils.RunPeachXml("dataExpression1.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == 'A12345', 'dataExpression1.xml failed, instead got [%s]' % repr(ret)


if __name__ == "__main__":
    unittest.main()

# end
