# -*- coding: utf8 -*-

'''
Several testcases around <String> and it's arguments.
'''

import unittest
import utils

def suite():
	suite = unittest.TestSuite()
	suite.addTest(AnalyzersBinaryTestCase())
	
	return suite

class AnalyzersBinaryTestCase(utils.PeachTcpTestCase):
	
	def runTest(self):
		# Test
		
		fd = open("analyzersBinary.bin", "rb+")
		data = fd.read()
		fd.close()
		
		self.peachUtils.RunPeachXml("analyzersBinary.xml")
		#self.peachUtils.RunDebugPeachXml("strings1.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == data, 'analyzersBinary.xml failed, instead [%s]' % repr(ret)
		
		
if __name__ == "__main__":
	unittest.main()

# end
