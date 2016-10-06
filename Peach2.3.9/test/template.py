
'''
Template for Peach test case

Complete this template then add the file to top of all.py.
'''

import unittest
import utils

def suite():
	suite = unittest.TestSuite()
	suite.addTest(TemplateTestCase1())  ## Update this line.
	suite.addTest(TemplateTestCase2())  ## Update this line, or add more as needed
	return suite

## Example of a test were the XML connects to us and send some data
## we then compare the data to the expected result.
class TemplateTestCase1(utils.PeachTcpTestCase):
	
	def runTest(self):
		self.peachUtils.RunPeachXml("template.xml")
		ret = self.peachUtils.GetListenerData()
		
		assert ret == 'PEACH', 'template.xml failed, instead got [%s]' % repr(ret)

## Just add more classes to add more tests
class TemplateTestCase2(utils.PeachTcpTestCase):
	
	def runTest(self):
		self.peachUtils.RunPeachXml("template.xml")
		ret = self.peachUtils.GetListenerData()
		
		assert ret == 'PEACH', 'template.xml failed, instead got [%s]' % repr(ret)


if __name__ == "__main__":
    unittest.main()

# end
