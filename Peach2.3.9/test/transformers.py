'''
Several testcases around <Transformer> and it's arguments.
'''

import unittest
import utils

def suite():
	suite = unittest.TestSuite()
	suite.addTest(TransformerEncodeTestCase())
	suite.addTest(TransformerEncode2TestCase())
	suite.addTest(TransformerEncode3TestCase())
	return suite

class TransformerEncodeTestCase(utils.PeachTcpTestCase):
	
	def runTest(self):
		# Test
		self.peachUtils.RunPeachXml("transformersEncode.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == 'MTIzNDU=', 'transformersEncode.xml failed, instead [%s]' % repr(ret)

class TransformerEncode2TestCase(utils.PeachTcpTestCase):
	
	def runTest(self):
		# Test
		self.peachUtils.RunPeachXml("transformersEncode2.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == 'gnzLDuqKcGxMNKFokfhOew==', 'transformersEncode2.xml failed, instead [%s]' % repr(ret)

class TransformerEncode3TestCase(utils.PeachTcpTestCase):
	
	def runTest(self):
		# Test
		self.peachUtils.RunPeachXml("transformersEncode3.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == '827ccb0eea8a706c4c34a16891f84e7b', 'transformersEncode3.xml failed, instead [%s]' % repr(ret)


if __name__ == "__main__":
    unittest.main()

# end
