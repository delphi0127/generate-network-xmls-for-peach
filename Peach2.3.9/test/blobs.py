'''
Some tests around Blob elements
'''

import unittest
import utils

def suite():
	suite = unittest.TestSuite()
	suite.addTest(BlobStringTestCase())  ## Update this line.
	suite.addTest(BlobHexTestCase())  ## Update this line, or add more as needed
	suite.addTest(BlobLiteralTestCase())  ## Update this line, or add more as needed
	return suite

class BlobStringTestCase(utils.PeachTcpTestCase):
	def runTest(self):
		self.peachUtils.RunPeachXml("blobsString.xml")
		ret = self.peachUtils.GetListenerData()
		
		assert ret == 'Peach', 'blobsString.xml failed, instead we got [%s]' % repr(ret)

class BlobHexTestCase(utils.PeachTcpTestCase):
	def runTest(self):
		self.peachUtils.RunPeachXml("blobsHex.xml")
		ret = self.peachUtils.GetListenerData()
		
		assert ret == 'Hello World', 'blobsHex.xml failed, instead we got [%s]' % repr(ret)

class BlobLiteralTestCase(utils.PeachTcpTestCase):
	def runTest(self):
		self.peachUtils.RunPeachXml("blobsLiteral.xml")
		ret = self.peachUtils.GetListenerData()
		
		assert ret == 'Peach World', 'blobsLiteral.xml failed, instead we got [%s]' % repr(ret)


if __name__ == "__main__":
    unittest.main()

# end
