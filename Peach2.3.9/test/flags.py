'''
Several testcases around <Flags> and <Flag>.
'''

import sys
sys.path.append("c:/peach")

from Peach.Generators.dictionary import *
from Peach.Generators.static import *
import unittest
import utils
import struct

def suite():
	suite = unittest.TestSuite()
	suite.addTest(FlagsInputTestCase())
	suite.addTest(FlagsOutputTestCase())
	#suite.addTest(Flags1TestCase())
	#suite.addTest(Flags2TestCase())
	#suite.addTest(Flags3TestCase())
	#suite.addTest(Flags4TestCase())
	#suite.addTest(Flags5TestCase())
	#suite.addTest(Flags6TestCase())
	suite.addTest(Flags7TestCase())
	suite.addTest(Flags8TestCase())
	return suite

class FlagsInputTestCase(utils.PeachSendAndRecvTestCase):
	
	def runTest(self):
		# Test
		
		gen = Flags2(None, 8, [ [0, 1, Static(1)], [1, 2, Static(2)], [3, 2, Static(3)], [5, 3, Static(4)] ])
		value = struct.pack("B", int(str(gen.getValue())))
		
		self.peachUtils.SetSendAndReceiveData(value)
		self.peachUtils.RunPeachXml("flagsInput.xml")
		ret = str(self.peachUtils.GetListenerData())
		
		assert ret == '4', 'flagsInput.xml failed, instead [%s]' % repr(ret)

class FlagsOutputTestCase(utils.PeachTcpTestCase):
	
	def runTest(self):
		# Test
		
		gen = Flags2(None, 8, [ [0, 1, Static(1)], [1, 2, Static(2)], [3, 2, Static(3)], [5, 3, Static(4)] ])
		value = struct.pack("B", int(str(gen.getValue())))
		
		self.peachUtils.RunPeachXml("flagsOutput.xml")
		ret = struct.unpack("B", str(self.peachUtils.GetListenerData()))[0]
		
		assert ret == 157, 'flagsOutput.xml failed, instead [%s]' % repr(ret)

#class Flags1TestCase(utils.PeachTcpTestCase):
#	
#	def runTest(self):
#		# Test
#		
#		self.peachUtils.RunPeachXml("flags1.xml")
#		ret = struct.unpack("B", str(self.peachUtils.GetListenerData()))[0]
#		
#		assert ret == 163, 'flags1.xml failed, instead [%s]' % repr(ret)
#
#class Flags2TestCase(utils.PeachTcpTestCase):
#	
#	def runTest(self):
#		# Test
#		
#		self.peachUtils.RunPeachXml("flags2.xml")
#		ret = struct.unpack("B", str(self.peachUtils.GetListenerData()))[0]
#		
#		assert ret == 131, 'flags2.xml failed, instead [%s]' % repr(ret)
#
#class Flags3TestCase(utils.PeachTcpTestCase):
#	
#	def runTest(self):
#		# Test
#		
#		self.peachUtils.RunPeachXml("flags3.xml")
#		ret = struct.unpack("!H", str(self.peachUtils.GetListenerData()))[0]
#		
#		assert ret == 65411, 'flags3.xml failed, instead [%s]' % repr(ret)
#
#class Flags4TestCase(utils.PeachTcpTestCase):
#	
#	def runTest(self):
#		# Test
#		
#		self.peachUtils.RunPeachXml("flags4.xml")
#		ret = struct.unpack("L", str(self.peachUtils.GetListenerData()))[0]
#		
#		assert ret == 2214560767, 'flags4.xml failed, instead [%s]' % repr(ret)
#
#class Flags5TestCase(utils.PeachTcpTestCase):
#	
#	def runTest(self):
#		# Test
#		
#		self.peachUtils.RunPeachXml("flags5.xml")
#		ret = struct.unpack("L", str(self.peachUtils.GetListenerData()))[0]
#		
#		assert ret == 33554432, 'flags5.xml failed, instead [%s]' % repr(ret)
#
#class Flags6TestCase(utils.PeachTcpTestCase):
#	
#	def runTest(self):
#		# Test
#		
#		self.peachUtils.RunPeachXml("flags6.xml")
#		ret = struct.unpack("B", str(self.peachUtils.GetListenerData()))[0]
#		
#		assert ret == 2, 'flags6.xml failed, instead [%s]' % repr(ret)

class Flags7TestCase(utils.PeachTcpTestCase):
	
	def runTest(self):
		# Test
		
		self.peachUtils.RunPeachXml("flags7.xml")
		ret = self.peachUtils.GetListenerData()
		
		assert ret == "\x28\x00\x28\x05\x8e\x01", 'flags7.xml failed, instead [%s]' % repr(ret)

class Flags8TestCase(utils.PeachTcpTestCase):
	
	def runTest(self):
		# Test
		
		self.peachUtils.RunPeachXml("flags8.xml")
		ret = self.peachUtils.GetListenerData()
		
		assert ret == "\x0a\x00\x0a\x50\x63\x10", 'flags8.xml failed, instead [%s]' % repr(ret)


if __name__ == "__main__":
	unittest.main()

# end
