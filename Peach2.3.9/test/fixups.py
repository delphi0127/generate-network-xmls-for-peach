'''
Misc test cases
'''

import unittest
import utils
from struct import pack, unpack

def suite():
	suite = unittest.TestSuite()
	suite.addTest(FixupTest1())
	suite.addTest(FixupTest2())
	suite.addTest(FixupTest3())
	return suite

class FixupTest1(utils.PeachTcpTestCase):
	def runTest(self):
		# Test
		self.peachUtils.RunPeachXml("fixups1.xml")
		ret = self.peachUtils.GetListenerData()
		data = "DAAAAAAAAAAyMzkwODIwMzk4NDVYewZM"
		assert ret == data, 'fixups1.xml failed. [%s]' % ret

class FixupTest2(utils.PeachTcpTestCase):
	def runTest(self):
		# Test
		self.peachUtils.RunPeachXml("fixups2.xml")
		ret = self.peachUtils.GetListenerData()
		data = "FAAAAAAAAAAyMzkwODIwMzk4NDVYewZM"
		assert ret == data, 'fixups2.xml failed. [%s]' % ret
	
class FixupTest3(utils.PeachTcpTestCase):
	def runTest(self):
		# Test
		self.peachUtils.RunPeachXml("fixups3.xml")
		ret = self.peachUtils.GetListenerData()
		data = "cnqZSaQ0E05ilAAAMjkwMTM0MDIxMzk3NDM5MDc0MTIzNDEyMw=="
		assert ret == data, 'fixups3.xml failed. [%s]' % ret


if __name__ == "__main__":
    unittest.main()

# end
