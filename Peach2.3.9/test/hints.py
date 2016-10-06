'''
Misc test cases
'''

import unittest
import utils
from struct import pack, unpack

def suite():
	suite = unittest.TestSuite()
	suite.addTest(HintXmlTestCase())
	return suite

class HintXmlTestCase(utils.PeachTcpTestCase):
	def runTest(self):
		# Test
		self.peachUtils.RunPeachXml("hintsXml.xml")
		ret = self.peachUtils.GetListenerData()
		fd = open("hintsXml.bin", "rb+")
		data = fd.read()
		fd.close()
		assert ret == data, 'hintsXml.xml failed.'


if __name__ == "__main__":
    unittest.main()

# end
