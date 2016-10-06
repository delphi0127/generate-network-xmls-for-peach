'''
Utils for unittests
'''

import unittest
import os
import socket
import win32con, time
from win32process import *
import threading

class Utils:
	
	pythonPath = "c:/python27/python.exe"

	localAgentPid = 0
	dataBuff = None
	localListener = None
	
	def StartLocalAgent(self):
		'''
		Start a local agent instance.
		'''
		(handle, hThread, dwProcessId, dwThreadId) = CreateProcess(None, self.pythonPath+' ../peach.py -a',
			None, None, 0, 0, None, None, STARTUPINFO())
		self.localAgentPid = handle
		#print "handle",self.localAgentPid
		time.sleep(1)
		return True
	
	def StopLocalAgent(self):
		'''
		Kill off the local agent
		'''
		#print "handle",self.localAgentPid
		TerminateProcess(self.localAgentPid, 0)
		return True
	
	def SpinUpListener(self):
		self.localListener = _listener()
		self.localListener.start()
		time.sleep(1)
	
	def GetListenerData(self):
		return self.localListener.dataBuff
	
	def TearDownListener(self):
		'''
		Stop listener and stop thread.  Currently we can't
		do this.  We just wait for the thread to end.
		'''
		self.localListener.join()
		self.localListener = None
	
	def SpinUpSendAndReceive(self):
		self.localListener = _sendAndRecv()
		self.localListener.start()
		time.sleep(1)
	
	def SetSendAndReceiveData(self, send):
		self.localListener.sendBuff = send
	
	def TearDownSendAndReceive(self):
		'''
		Stop listener and stop thread.  Currently we can't
		do this.  We just wait for the thread to end.
		'''
		self.localListener.join()
		self.localListener = None
	
	def SpinUpSend(self):
		self.localListener = _send()
		self.localListener.start()
		time.sleep(1)
	
	def SetSendData(self, send):
		self.localListener.sendBuff = send
	
	def TearDownSend(self):
		'''
		Stop listener and stop thread.  Currently we can't
		do this.  We just wait for the thread to end.
		'''
		self.localListener.join()
		self.localListener = None
	
	def RunPeachXml(self, xml):
		'''
		Returns true or false depending on how 'peach.py xml' goes.
		'''
		args = ['python', '../peach.py', xml]
		ret = os.spawnv(os.P_WAIT, self.pythonPath, args)
		return ret == 0
	
	def RunDebugPeachXml(self, xml):
		'''
		Returns true or false depending on how 'peach.py xml' goes.
		'''
		args = ['python', '../peach.py', '--debug', xml]
		ret = os.spawnv(os.P_WAIT, self.pythonPath, args)
		return ret == 0
	
	def TestPeachXml(self, xml):
		'''
		Returns true or false depending on how 'peach.py -t xml' goes.
		'''
		args = ['python', '../peach.py', '-t', xml]
		ret = os.spawnv(os.P_WAIT, self.pythonPath, args)
		return ret == 0
	
	def CountPeachXml(self, xml):
		'''
		Returns true or false depending on how 'peach.pyh -c xml' goes.
		'''
		args = ['python', '../peach.py', '-c', xml]
		ret = os.spawnv(os.P_WAIT, self.pythonPath, args)
		return ret == 0

		
class _sendAndRecv(threading.Thread):
	'''
	Note currently we block listening.
	'''
	
	sendBuff = None
	dataBuff = None
	
	def run(self):
		HOST = ''
		PORT = 9001
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind((HOST, PORT))
		s.listen(1)
		conn, addr = s.accept()
		
		print "Sending: [%s]" % repr(self.sendBuff)
		conn.send(self.sendBuff)
		
		self.dataBuff = ''
		while 1:
			data = conn.recv(1024)
			if not data: break
			self.dataBuff += data
		conn.close()
		print "Receiving: [%s]" % repr(self.dataBuff)

class _send(threading.Thread):
	'''
	Note currently we block listening.
	'''
	
	sendBuff = None
	
	def run(self):
		HOST = ''
		PORT = 9001
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind((HOST, PORT))
		s.listen(1)
		conn, addr = s.accept()
		
		print "Sending: [%s]" % repr(self.sendBuff)
		conn.send(self.sendBuff)

class _listener(threading.Thread):
	'''
	Note currently we block listening.
	'''
	def run(self):
		HOST = ''
		PORT = 9001
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind((HOST, PORT))
		s.listen(1)
		conn, addr = s.accept()
		#print 'Connected by', addr
		self.dataBuff = ''
		while 1:
			data = conn.recv(1024)
			if not data: break
			self.dataBuff += data
		conn.close()
		#print "DATA: [%s]" % repr(self.dataBuff)

class PeachTestCase(unittest.TestCase):
	def setUp(self):
		self.peachUtils = Utils()
		self.peachUtils.StartLocalAgent()
	
	def tearDown(self):
		self.peachUtils.StopLocalAgent()

class PeachTestCaseNoAgent(unittest.TestCase):
	def setUp(self):
		self.peachUtils = Utils()

class PeachTcpTestCase(PeachTestCase):
	def setUp(self):
		PeachTestCase.setUp(self)
		self.peachUtils.SpinUpListener()
	
	def tearDown(self):
		PeachTestCase.tearDown(self)
		self.peachUtils.TearDownListener()

class PeachSendAndRecvTestCase(PeachTestCase):
	def setUp(self):
		PeachTestCase.setUp(self)
		self.peachUtils.SpinUpSendAndReceive()
	
	def tearDown(self):
		PeachTestCase.tearDown(self)
		self.peachUtils.TearDownSendAndReceive()

class PeachSendTestCase(PeachTestCase):
	def setUp(self):
		PeachTestCase.setUp(self)
		self.peachUtils.SpinUpSend()
	
	def tearDown(self):
		PeachTestCase.tearDown(self)
		self.peachUtils.TearDownSend()

# end
