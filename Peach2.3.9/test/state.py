'''
StateMachine unittests.
'''

import unittest
import utils
import sys
sys.path.append("..")
import helpers
from Peach.Engine.engine import Engine

def suite():
	suite = unittest.TestSuite()
	suite.addTest(StateSlurpTestCase1())
	suite.addTest(StateSlurpTestCase2())
	suite.addTest(StateSlurpTestCase3())
	suite.addTest(StateWhenTestCase())
	suite.addTest(StateChangeStateTestCase())
	suite.addTest(StateChangeState2TestCase())
	suite.addTest(StateData1TestCase())
	suite.addTest(StateData2TestCase())
	suite.addTest(StateData3TestCase())
	suite.addTest(StateData4TestCase())
	suite.addTest(StateCall1TestCase())
	suite.addTest(StateCall2TestCase())
	suite.addTest(StateCall3TestCase())
	suite.addTest(StateProperty1TestCase())
	#suite.addTest(StateHttp1TestCase())
	
	return suite

class StateSlurpTestCase1(utils.PeachSendAndRecvTestCase):
	def runTest(self):
		self.peachUtils.SetSendAndReceiveData("0987654321")
		self.peachUtils.RunPeachXml("stateSlurp1.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == '0987654321', 'stateSlurp1.xml failed, instead got [%s]' % repr(ret)

class StateSlurpTestCase2(utils.PeachSendAndRecvTestCase):
	def runTest(self):
		self.peachUtils.SetSendAndReceiveData("0987654321")
		self.peachUtils.RunPeachXml("stateSlurp2.xml")
		#self.peachUtils.RunDebugPeachXml("stateSlurp2.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == '5432109876', 'stateSlurp2.xml failed, instead got [%s]' % repr(ret)

class StateSlurpTestCase3(utils.PeachTcpTestCase):
	def runTest(self):
		self.peachUtils.RunPeachXml("stateSlurp3.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == 'INITIAL   STATE4    ', 'stateSlurp3.xml failed, instead [%s]' % repr(ret)

class StateWhenTestCase(utils.PeachSendAndRecvTestCase):
	def runTest(self):
		self.peachUtils.SetSendAndReceiveData("State2    ")
		self.peachUtils.RunPeachXml("stateWhen.xml")
		#self.peachUtils.RunDebugPeachXml("stateWhen.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == 'STATE2    ', 'stateWhen.xml failed, instead got [%s]' % repr(ret)

class StateChangeStateTestCase(utils.PeachTcpTestCase):
	def runTest(self):
		self.peachUtils.RunPeachXml("stateChangeState.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == 'STATE4    ', 'stateChangeState.xml failed, instead [%s]' % repr(ret)

class StateChangeState2TestCase(utils.PeachTcpTestCase):
	def runTest(self):
		self.peachUtils.RunPeachXml("stateChangeState2.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == 'INITIAL   STATE4    ', 'stateChangeState2.xml failed, instead [%s]' % repr(ret)

class StateData1TestCase(utils.PeachTcpTestCase):
	def runTest(self):
		self.peachUtils.RunPeachXml("stateData1.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == 'Data1     ', 'stateData1.xml failed, instead [%s]' % repr(ret)

class StateData2TestCase(utils.PeachTcpTestCase):
	def runTest(self):
		self.peachUtils.RunPeachXml("stateData2.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == 'Data1     Data2     ', 'stateData2.xml failed, instead [%s]' % repr(ret)

class StateData3TestCase(utils.PeachTcpTestCase):
	def runTest(self):
		self.peachUtils.RunPeachXml("stateData3.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == 'Data1     ', 'stateData3.xml failed, instead [%s]' % repr(ret)

class StateData4TestCase(utils.PeachTcpTestCase):
	def runTest(self):
		self.peachUtils.RunPeachXml("stateData4.xml")
		ret = self.peachUtils.GetListenerData()
		assert ret == 'INITIAL   HELLO THER', 'stateData4.xml failed, instead [%s]' % repr(ret)

class StateCall1TestCase(utils.PeachTestCase):	
	def runTest(self):
		#self.peachUtils = utils.Utils()
		self.peachUtils.RunPeachXml("stateCall1.xml")
		assert True, "stateCall1.xml failed"

class StateCall2TestCase(utils.PeachTestCase):	
	def runTest(self):
		#self.peachUtils = utils.Utils()
		self.peachUtils.RunPeachXml("stateCall2.xml")
		assert True, "stateCall2.xml failed"

class StateCall3TestCase(utils.PeachTestCase):	
	def runTest(self):
		self.peachUtils.RunPeachXml("stateCall3.xml")
		assert True, "stateCall3.xml failed"

class StateProperty1TestCase(utils.PeachTestCase):	
	def runTest(self):
		engine = Engine()
		engine.Run("file:stateProperty1.xml")

### This is also a test in Incoming, is a TODO item for now.
##class StateHttp1TestCase(utils.PeachSendAndRecvTestCase):
##	def runTest(self):
##		self.peachUtils.SetSendAndReceiveData("""HTTP/1.1 302 Object moved\r\nServer: Microsoft-IIS/5.1\r\nDate: Fri, 07 Mar 2008 04:54:39 GMT\r\nX-Powered-By: ASP.NET\r\nLocation: localstart.asp\r\nConnection: Keep-Alive\r\nContent-Length: 121\r\nContent-Type: text/html\r\nSet-Cookie: ASPSESSIONIDSSBDSTTR=MCOHEFGAADAHPPHEDFKLMEFH; path=/\r\nCache-control: private\r\n\r\n<head><title>Object moved</title></head>\r\n<body><h1>Object Moved</h1>This object may be found <a HREF="">here</a>.</body>\r\n""")
##		self.peachUtils.RunPeachXml("stateHttp.xml")
##		ret = self.peachUtils.GetListenerData()
##		assert ret == 'GET / HTTP/1.0\r\n\r\n', 'stateHttp.xml failed, instead got [%s]' % repr(ret)


if __name__ == "__main__":
    unittest.main()



# end
