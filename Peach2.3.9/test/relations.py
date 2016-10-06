'''
Several testcases around <Relation> and it's arguments.
'''

import unittest
import utils

def suite():
	suite = unittest.TestSuite()
	suite.addTest(RelationSize1TestCase())
	suite.addTest(RelationSize2TestCase())
	suite.addTest(RelationSize3TestCase())
	suite.addTest(RelationSize4TestCase())
	suite.addTest(RelationSize5TestCase())
	##suite.addTest(RelationSize6TestCase())
	##suite.addTest(RelationSize7TestCase())
	suite.addTest(RelationCount1TestCase())
	suite.addTest(RelationCount2TestCase())
	suite.addTest(RelationCount3TestCase())
	suite.addTest(RelationCount4TestCase())
	return suite

class RelationSize1TestCase(utils.PeachTcpTestCase):
	
	def runTest(self):
		# Test
		self.peachUtils.RunPeachXml("relationsSize1.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == '12Hello World!', 'relationsSize1.xml failed, instead [%s]' % repr(ret)

class RelationSize2TestCase(utils.PeachTcpTestCase):
	
	def runTest(self):
		# Test
		self.peachUtils.RunPeachXml("relationsSize2.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == '\x0cHello World!', 'relationsSize2.xml failed, instead [%s]' % repr(ret)

class RelationSize3TestCase(utils.PeachTcpTestCase):
	
	def runTest(self):
		# Test
		self.peachUtils.RunPeachXml("relationsSize3.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == '\x11\x0cHello World!12345', 'relationsSize3.xml failed, instead [%s]' % repr(ret)

class RelationSize4TestCase(utils.PeachTcpTestCase):
	
	def runTest(self):
		# Test
		self.peachUtils.RunPeachXml("relationsSize4.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == '\x11\x0c\x14Hello World!1234518string from model1', 'relationsSize4.xml failed, instead [%s]' % repr(ret)

class RelationSize5TestCase(utils.PeachTcpTestCase):
	
	def runTest(self):
		# Test
		self.peachUtils.RunPeachXml("relationsSize5.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == '\x0B1234567890', 'relationsSize5.xml failed, instead [%s]' % repr(ret)

#class RelationSize6TestCase(utils.PeachTcpTestCase):
#	
#	def runTest(self):
#		# Test
#		self.peachUtils.RunPeachXml("relationsSize6.xml")
#		ret = self.peachUtils.GetListenerData()
#		assert ret == '60Hello World!Hello World!Hello World!Hello World!Hello World!', 'relationsSize6.xml failed, instead [%s]' % repr(ret)
#
#class RelationSize7TestCase(utils.PeachTcpTestCase):
#	
#	def runTest(self):
#		# Test
#		self.peachUtils.RunPeachXml("relationsSize7.xml")
#		ret = self.peachUtils.GetListenerData()
#		assert ret == '36Hello World!Hello World!Hello World!', 'relationsSize7.xml failed, instead [%s]' % repr(ret)

class RelationCount1TestCase(utils.PeachTcpTestCase):
	
	def runTest(self):
		# Test
		self.peachUtils.RunPeachXml("relationsCount1.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == '3Hello World!Hello World!Hello World!', 'relationsCount1.xml failed, instead [%s]' % repr(ret)

class RelationCount2TestCase(utils.PeachTcpTestCase):
	
	def runTest(self):
		# Test
		self.peachUtils.RunPeachXml("relationsCount2.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == '4Hello World!Hello World!Hello World!Hello World!', 'relationsCount2.xml failed, instead [%s]' % repr(ret)

class RelationCount3TestCase(utils.PeachTcpTestCase):
	
	def runTest(self):
		# Test
		self.peachUtils.RunPeachXml("relationsCount3.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == '5Hello World!Hello World!Hello World!Hello World!Hello World!', 'relationsCount3.xml failed, instead [%s]' % repr(ret)

class RelationCount4TestCase(utils.PeachTcpTestCase):
	
	def runTest(self):
		# Test
		self.peachUtils.RunPeachXml("relationsCount4.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == '\x03Hello World!Hello World!Hello World!', 'relationsCount4.xml failed, instead [%s]' % repr(ret)



if __name__ == "__main__":
	unittest.main()

# end
