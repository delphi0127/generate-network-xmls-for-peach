
'''
Perform variouse tests around parsing of Peach XML files.
'''

import unittest
import utils
import os.path

def suite():
	suite = unittest.TestSuite()
	suite.addTest(ParsingTestCases())
	return suite

class ParsingTestCases(unittest.TestCase):
	
	def runTest(self):
		baseName = "parsingTest%d.xml"
		
		self.peachUtils = utils.Utils()
		
		num = 1
		while os.path.exists(baseName % num):
			fileName = baseName % num
			assert self.peachUtils.TestPeachXml(fileName) == True, "Failed to test %s" % fileName
			num += 1
		
		baseName = "parsingCount%d.xml"
		
		num = 1
		while os.path.exists(baseName % num):
			fileName = baseName % num
			assert self.peachUtils.TestPeachXml(fileName) == True, "Failed to test %s" % fileName
			num += 1

if __name__ == "__main__":
    unittest.main()

# end
