'''
Several testcases around the file publishers.
'''

import unittest
import utils
import os

def suite():
	suite = unittest.TestSuite()
	suite.addTest(PublishersFileReaderTestCase())
	suite.addTest(PublishersFileReader2TestCase())
	suite.addTest(PublishersFileWriterTestCase())
	suite.addTest(PublishersFilePerIterationTestCase())
	return suite

class PublishersFileReaderTestCase(utils.PeachTestCase):
	'''Currently there is no real way to see if this worked
	'''
	
	def runTest(self):
		# Test
		self.peachUtils.RunPeachXml("publishersFileReader.xml")
		assert True, 'publishersFileReader.xml failed, instead []'

class PublishersFileReader2TestCase(utils.PeachTestCase):
	'''Currently there is no real way to see if this worked
	'''
	
	def runTest(self):
		# Test
		self.peachUtils.RunPeachXml("publishersFileReader2.xml")
		assert True, 'publishersFileReader2.xml failed, instead []'

class PublishersFileWriterTestCase(utils.PeachTestCase):
	
	def runTest(self):
		# Test
		
		# 1. Delete possibly old file
		try:
			os.unlink("publishersFileWriter.dat")
		except:
			pass
		
		self.peachUtils.RunPeachXml("publishersFileWriter.xml")
		
		ret = None
		try:
			fd = open("publishersFileWriter.dat")
			ret = fd.read()
			fd.close()
			os.unlink("publishersFileWriter.dat")
		except:
			assert False, 'publishersFileWriter.xml did not generate file'
		
		assert ret == "12345abcd", 'publishersFileWriter.xml failed, instead [%s]' % repr(ret)

class PublishersFilePerIterationTestCase(utils.PeachTestCase):
	
	def runTest(self):
		# Test
		
		# 1. Delete possibly old file
		try:
			os.unlink("FilePerIteration/publishersFilePerIteration_0.dat")
		except:
			pass
		
		try:
			os.rmdir("FilePerIteration")
		except:
			pass
		
		self.peachUtils.RunPeachXml("publishersFilePerIteration.xml")
		
		ret = None
		try:
			fd = open("FilePerIteration/publishersFilePerIteration_0.dat")
			ret = fd.read()
			fd.close()
		except:
			assert False, 'publishersFilePerIteration.xml did not generate file'
		
		try:
			os.unlink("FilePerIteration/publishersFilePerIteration_0.dat")
			os.rmdir("FilePerIteration")
		except:
			pass
		
		assert ret == "12345abcd", 'publishersFilePerIteration.xml failed, instead [%s]' % repr(ret)
		
if __name__ == "__main__":
    unittest.main()

# end
