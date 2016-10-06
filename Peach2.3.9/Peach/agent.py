
'''
Peach Agent

This is the Peach Agent program.  Peach supports both local
and remote agents that can perform variouse actions such
as monitor something (network, proccess) or perform other
actions such as restart a vm.

@author: Michael Eddington
@version: $Id: agent.py 2745 2012-03-13 23:54:58Z meddingt $
'''

#
# Copyright (c) Michael Eddington
#
# Permission is hereby granted, free of charge, to any person obtaining a copy 
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights 
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
# copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in	
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

# Authors:
#   Michael Eddington (mike@phed.org)

# $Id: agent.py 2745 2012-03-13 23:54:58Z meddingt $

import sys, os, time, uuid, re
import socket, types
import cPickle as pickle
from twisted.web import xmlrpc, server
from xmlrpclib import ServerProxy, Error
from Peach.Publishers import *
from Peach.Engine.common import *

def Debug(msg):
	#print msg
	pass

def PeachStr(s):
	'''
	Our implementation of str() which does not
	convert None to 'None'.
	'''
	
	if s == None:
		return None
	
	return str(s)

class Monitor:
	'''
	Extend from this to implement a Monitor.  Monitors are
	run by an Agent and must operate in an async mannor.  Any
	blocking tasks must be performed in another thread.
	'''
	
	def __init__(self, args):
		'''
		Constructor.  Arguments are supplied via the Peach XML
		file.
		
		@type	args: Dictionary
		@param	args: Dictionary of parameters
		'''
		
		# Our name for this monitor
		self._name = None
	
	def OnTestStarting(self):
		'''
		Called right before start of test case or variation
		'''
		pass
	
	def OnTestFinished(self):
		'''
		Called right after a test case or varation
		'''
		pass
	
	def GetMonitorData(self):
		'''
		Get any monitored data from a test case.
		'''
		return None
	
	def RedoTest(self):
		'''
		Should the current test be reperformed.
		'''
		return False
	
	def DetectedFault(self):
		'''
		Check if a fault was detected.
		'''
		return False
	
	def OnFault(self):
		'''
		Called when a fault was detected.
		'''
		pass
	
	def OnShutdown(self):
		'''
		Called when Agent is shutting down, typically at end
		of a test run or when a Stop-Run occurs
		'''
		pass
	
	def StopRun(self):
		'''
		Return True to force test run to fail.  This
		should return True if an unrecoverable error
		occurs.
		'''
		return False
	
	def PublisherCall(self, method):
		'''
		Called when a call action is being performed.  Call
		actions are used to launch programs, this gives the
		monitor a chance to determin if it should be running
		the program under a debugger instead.
		
		Note: This is a bit of a hack to get this working
		'''
		pass


# Need to define Monitor before we do this include!
from Peach.Agent import *

class _MsgType:
	'''
	Type of message
	'''
	
	ClientHello = 2			#: Sent by fuzzer, will include password (optional)
	AgentHello = 1			#: Sent if password okay, else drop
	
	ClientDisconnect = 5
	AgentDisconnect = 6
	
	AgentReady = 7
	
	Ack = 17				#: Ack that we completed and finished
	Nack = 18				#: Ack that we did not complete, error occured
							#: exception in msg.exception
	## Monitors
	
	GetMonitorData = 11
	DetectFault = 8
	OnFault = 9
	OnShutdown = 10			#: Test completed, shutting down
	OnTestStarting = 13		#: On Test Case Starting
	OnTestFinished = 14		#: On Test Case Finished
	StopRun = 20
	RedoTest = 30			#: Should we re-perform the current test?
	
	StartMonitor = 15		#: Startup a monitor
	# Expect a msg.monitorName: str, msg.monitorClass: str and msg.params: dictionary
	StopMonitor = 16		#: Stop a monitor
	
	## Publishers
	
	PublisherStart = 21
	PublisherStop = 22
	PublisherAccept = 23
	PublisherConnect = 24
	PublisherClose = 25
	PublisherCall = 26		#: Notify that we are running a call action
	PublisherProperty = 27	#: Notify that we are running a property action
	PublisherSend = 28
	PublisherReceive = 29
	


class _Msg:
	'''
	This is a message holder that is serialized and sent over
	the named pipe.
	'''
	
	def __init__(self, id, type, results = None):
		self.id = id
		self.type = type
		self.results = results
		self.stopRun = False
		self.password = False
		self.pythonPaths = None
		self.imports = None

class Agent:
	'''
	A remote or local Agent that listens on a named pipe.  Each agent
	can only be connected to by a single Peach Fuzzer.
	'''
	
	def __init__(self, password = None, port = 9000):
		'''
		Creates and Agent instance and attemps to connect
		to the AgentMaster.  If connection works the Client Hello message
		is sent.
		
		@type	password: string
		@param	password: Password to use
		'''
		
		from twisted.internet import reactor
		agent = AgentXmlRpc()
		
		agent._password = password
		agent._monitors = []
		agent._publishers = {}
		agent._id = None
		
		print "] Peach Agent\n"
		
		if agent._password != None:
			print "\n //-> Listening on [%s] with password [%s]\n" % (port, agent._password)
		else:
			print "\n //-> Listening on [%s] with no password\n" % (port)
		
		reactor.listenTCP(port, server.Site(agent))
		reactor.run()


class AgentXmlRpc(xmlrpc.XMLRPC):
	
	def xmlrpc_clientHello(self, msg):
		msg = pickle.loads(msg)
		if msg.password != self._password:
			print "Agent: Incorrect password on clientHello [%s]" % msg.password
			return pickle.dumps(_Msg(None, _MsgType.Nack))
		
		if msg.type != _MsgType.ClientHello:
			return pickle.dumps(_Msg(None, _MsgType.Nack))
		
		print "Agent: clientHello()"
		
		if self._id != None:
			self._stopAllMonitors()
		
		self._id = str(uuid.uuid1())
		print "Agent: Session ID: ", self._id
		
		# Handle any PythonPath or Imports
		if msg.pythonPaths != None:
			for p in msg.pythonPaths:
				sys.path.append(p['name'])
		
		if msg.imports != None:
			for i in msg.imports:
				self._handleImport(i)
		
		print "Agent: clientHello() all done"
		
		return pickle.dumps(_Msg(self._id, _MsgType.AgentHello))

	def GetClassesInModule(self, module):
		'''
		Return array of class names in module
		'''
		
		classes = []
		for item in dir(module):
			i = getattr(module, item)
			if type(i) == types.ClassType and item[0] != '_':
				classes.append(item)
		
		return classes
	
	def _handleImport(self, i):
		
		importStr = i['import']
		
		if i['from'] != None and len(i['from']) > 0:
			fromStr = i['from']
			
			if importStr == "*":
				module = __import__(PeachStr(fromStr), globals(), locals(), [ PeachStr(importStr) ], -1)
				
				try:
					# If we are a module with other modules in us then we have an __all__
					for item in module.__all__:
						globals()[item] = getattr(module, item)
					
				except:
					# Else we just have some classes in us with no __all__
					for item in self.GetClassesInModule(module):
						globals()[item] = getattr(module, item)
				
			else:
				module = __import__(PeachStr(fromStr), globals(), locals(), [ PeachStr(importStr) ], -1)
				for item in importStr.split(','):
					item = item.strip()
					globals()[item] = getattr(module, item)
		
		else:
			globals()[importStr] = __import__(PeachStr(importStr), globals(), locals(), [], -1)
	
	
	def xmlrpc_clientDisconnect(self, msg):
		msg = pickle.loads(msg)
		if self._id == None or msg.id != self._id:
			return pickle.dumps(_Msg(None, _MsgType.Nack))
		
		if msg.type != _MsgType.ClientDisconnect:
			return pickle.dumps(_Msg(None, _MsgType.Nack))
		
		print "Agent: clientDisconnect()"
		
		self._stopAllMonitors()
		return pickle.dumps(_Msg(None, _MsgType.Ack))
	
	def xmlrpc_stopRun(self, msg):
		msg = pickle.loads(msg)
		if self._id == None or msg.id != self._id:
			return pickle.dumps(_Msg(None, _MsgType.Nack))
		
		if msg.type != _MsgType.StopRun:
			return pickle.dumps(_Msg(None, _MsgType.Nack))
		
		print "Agent: stopRun()"
		
		msg = _Msg(None, _MsgType.Ack)
		msg.results = False
		
		for m in self._monitors:
			if m.StopRun():
				print "Agent: Stop run request!"
				msg.results = True
		
		return pickle.dumps(msg)
	
	def xmlrpc_detectFault(self, msg):
		msg = pickle.loads(msg)
		if self._id == None or msg.id != self._id:
			return pickle.dumps(_Msg(None, _MsgType.Nack))
		
		if msg.type != _MsgType.DetectFault:
			return pickle.dumps(_Msg(None, _MsgType.Nack))
		
		print "Agent: detectFault()"
		
		msg = _Msg(None, _MsgType.Ack)
		msg.results = False
		
		for m in self._monitors:
			if m.DetectedFault():
				print "Agent: Detected fault!"
				msg.results = True
		
		print "Agent: Sending detectFault result [%s]" % repr(msg.results)
		return pickle.dumps(msg)
	
	def xmlrpc_redoTest(self, msg):
		msg = pickle.loads(msg)
		if self._id == None or msg.id != self._id:
			return pickle.dumps(_Msg(None, _MsgType.Nack))
		
		if msg.type != _MsgType.RedoTest:
			return pickle.dumps(_Msg(None, _MsgType.Nack))
		
		print "Agent: redoTest()"
		
		msg = _Msg(None, _MsgType.Ack)
		msg.results = False
		
		for m in self._monitors:
			if m.RedoTest():
				msg.results = True
		
		print "Agent: Sending redoTest result [%s]" % repr(msg.results)
		return pickle.dumps(msg)
	
	def xmlrpc_getMonitorData(self, msg):
		msg = pickle.loads(msg)
		if self._id == None or msg.id != self._id:
			return pickle.dumps(_Msg(None, _MsgType.Nack))
		
		if msg.type != _MsgType.GetMonitorData:
			return pickle.dumps(_Msg(None, _MsgType.Nack))
		
		print "Agent: getMonitorData()"
		
		msg = _Msg(None, _MsgType.Ack)
		msg.results = []
		
		for m in self._monitors:
			try:
				data = m.GetMonitorData()
				if data != None:
					msg.results.append(data)
				
			except:
				print "Agent: getMonitorData: Failrue getting data from:", m.monitorName
				raise
				#pass
		
		return pickle.dumps(msg)
	
	def xmlrpc_onFault(self, msg):
		msg = pickle.loads(msg)
		if self._id == None or msg.id != self._id:
			return pickle.dumps(_Msg(None, _MsgType.Nack))
		
		if msg.type != _MsgType.OnFault:
			return pickle.dumps(_Msg(None, _MsgType.Nack))
		
		print "Agent: onFault()"
		
		for m in self._monitors:
			m.OnFault()
		
		return pickle.dumps(_Msg(None, _MsgType.Ack))
	
	def xmlrpc_onTestFinished(self, msg):
		msg = pickle.loads(msg)
		if self._id == None or msg.id != self._id:
			return pickle.dumps(_Msg(None, _MsgType.Nack))
		
		if msg.type != _MsgType.OnTestFinished:
			return pickle.dumps(_Msg(None, _MsgType.Nack))
		
		print "Agent: onTestFinished()"
		
		for m in self._monitors:
			m.OnTestFinished()
		
		return pickle.dumps(_Msg(None, _MsgType.Ack))
	
	def xmlrpc_onTestStarting(self, msg):
		msg = pickle.loads(msg)
		if self._id == None or msg.id != self._id:
			return pickle.dumps(_Msg(None, _MsgType.Nack))
		
		if msg.type != _MsgType.OnTestStarting:
			return pickle.dumps(_Msg(None, _MsgType.Nack))
		
		print "Agent: onTestStarting()"
		
		for m in self._monitors:
			m.OnTestStarting()
		
		return pickle.dumps(_Msg(None, _MsgType.Ack))

	def xmlrpc_onPublisherCall(self, msg):
		msg = pickle.loads(msg)
		if self._id == None or msg.id != self._id:
			return pickle.dumps(_Msg(None, _MsgType.Nack))
		
		if msg.type != _MsgType.PublisherCall:
			return pickle.dumps(_Msg(None, _MsgType.Nack))
		
		print "Agent: onPublisherCall():", msg.method
		
		outRet = None
		for m in self._monitors:
			ret = m.PublisherCall(msg.method)
			if ret != None:
				outRet = ret
		
		return pickle.dumps(_Msg(None, _MsgType.Ack, outRet))

	def _stopAllMonitors(self):
		'''
		Stop all monitors.  Part of resetting
		our connection.
		'''
		
		for m in self._monitors:
			m.OnShutdown()
		
		self._monitors = []
	
	def xmlrpc_onShutdown(self, msg):
		msg = pickle.loads(msg)
		if self._id == None or msg.id != self._id:
			return pickle.dumps(_Msg(None, _MsgType.Nack))
		
		if msg.type != _MsgType.OnShutdown:
			return pickle.dumps(_Msg(None, _MsgType.Nack))
		
		print "Agent: onShutdown()"
		
		self._stopAllMonitors()
		return pickle.dumps(_Msg(None, _MsgType.Ack))
	
	def xmlrpc_stopMonitor(self, msg):
		msg = pickle.loads(msg)
		if self._id == None or msg.id != self._id:
			return pickle.dumps(_Msg(None, _MsgType.Nack))
		
		if msg.type != _MsgType.StopMonitor:
			return pickle.dumps(_Msg(None, _MsgType.Nack))
		
		print "Agent: stopMonitor(%s)" % msg.monitorName
		
		for i in xrange(len(self._monitors)):
			m = self._monitors[i]
			if m._name == msg.monitorName:
				
				try:
					m.OnShutdown()
				except:
					pass
				
				self._monitors.remove(m)
				break
		
		return pickle.dumps(_Msg(None, _MsgType.Ack))
		
	def xmlrpc_startMonitor(self, msg):
		msg = pickle.loads(msg)
		if self._id == None or msg.id != self._id:
			return pickle.dumps(_Msg(None, _MsgType.Nack))
		
		if msg.type != _MsgType.StartMonitor:
			return pickle.dumps(_Msg(None, _MsgType.Nack))
		
		print "Agent: startMonitor(%s)" % msg.monitorName
		
		try:
			code = msg.monitorClass + "(msg.params)"
			print "code:", code
			monitor = eval(code)
			
			if monitor == None:
				print "Agent: Unable to create Monitor [%s]" % msg.monitorClass
				return pickle.dumps(_Msg(self._id, _MsgType.Nack, "Unable to create Monitor [%s]" % msg.monitorClass))
			
			monitor.monitorName = msg.monitorName
			self._monitors.append(monitor)
			
			print "Agent: Sending Ack"
			return pickle.dumps(_Msg(None, _MsgType.Ack))
			
		except:
			print "Agent: Unable to create Monitor [%s], exception occured." % msg.monitorClass
			raise
			return pickle.dumps(_Msg(None, _MsgType.Nack, "Unable to create Monitor [%s], exception occured." % msg.monitorClass))

	## Publishers ######################################################
	
	def xmlrpc_publisherInitialize(self, id, name, cls, *args):
		if self._id == None or id != self._id:
			print "xmlrpc_publisherInitialize: Can't validate clients session id"
			return -1
		
		print "Agent: xmlrpc_publisherInitialize(%s, %s)" % (name, cls)
		
		try:
			code = cls + "("
			for cnt in range(len(args[0])):
				code += "args[0][%d]," % cnt
			code = code[:-1] + ")"
			
			print "Agent: Code: %s" % code
			publisher = eval(code)
			
			if publisher == None:
				print "Agent: Unable to create Publisher [%s]" % cls
				return -2
			
			publisher.publisherName = name
			self._publishers[name] = publisher
			
			print "Agent: Publisher created okay!"
			return 0
			
		except:
			print "Agent: Unable to create Publisher [%s], exception occured." % cls
			return -2

	def xmlrpc_publisherStart(self, id, name):
		if self._id == None or id != self._id:
			print "xmlrpc_publisherStart: Can't validate clients session id"
			return -1
		
		if name not in self._publishers:
			return -2
		
		self._publishers[name].start()
		return 0

	def xmlrpc_publisherStop(self, id, name):
		if self._id == None or id != self._id:
			print "xmlrpc_publisherStop: Can't validate clients session id"
			return -1
		
		if name not in self._publishers:
			return -2
		
		self._publishers[name].stop()
		return 0

	def xmlrpc_publisherAccept(self, id, name):
		if self._id == None or id != self._id:
			print "xmlrpc_publisherAccept: Can't validate clients session id"
			return -1
		
		if name not in self._publishers:
			return -2
		
		self._publishers[name].accept()
		return 0

	def xmlrpc_publisherConnect(self, id, name):
		if self._id == None or id != self._id:
			print "xmlrpc_publisherConnect: Can't validate clients session id"
			return -1
		
		if name not in self._publishers:
			return -2
		
		self._publishers[name].connect()
		return 0

	def xmlrpc_publisherClose(self, id, name):
		if self._id == None or id != self._id:
			print "xmlrpc_publisherClose: Can't validate clients session id"
			return -1
		
		if name not in self._publishers:
			return -2
		
		self._publishers[name].close()
		return 0

	def xmlrpc_publisherCall(self, id, name, method, args):
		if self._id == None or id != self._id:
			print "xmlrpc_publisherCall: Can't validate clients session id"
			return -1
		
		if name not in self._publishers:
			return -2
		
		args = pickle.loads(args)
		
		ret = self._publishers[name].call(method, args)
		if ret == None:
			return 0
		return ret

	def xmlrpc_publisherProperty(self, id, name, property, value):
		if self._id == None or id != self._id:
			print "xmlrpc_publisherProperty: Can't validate clients session id"
			return -1
		
		if name not in self._publishers:
			return -2
		
		value = pickle.loads(value)
		
		ret = self._publishers[name].property(property, value)
		if ret == None:
			return 0
		return ret

	def xmlrpc_publisherSend(self, id, name, data):
		if self._id == None or id != self._id:
			print "xmlrpc_publisherSend: Can't validate clients session id"
			return -1
		
		if name not in self._publishers:
			return -2
		
		value = pickle.loads(data)
		
		ret = self._publishers[name].send(data)
		if ret == None:
			return 0
		return ret

	def xmlrpc_publisherReceive(self, id, name, size):
		if self._id == None or id != self._id:
			print "xmlrpc_publisherReceive: Can't validate clients session id"
			return -1
		
		if name not in self._publishers:
			return -2
		
		return self._publishers[name].receive(size)

import imp, os, sys, subprocess

try:
	import win32process
	import win32con
except:
	pass

class AgentClient:
	'''
	An Agent client.  Clients connect and send/recieve messages with
	a single remote Agent.
	'''
	def __init__(self, agentUri, password, pythonPaths = None, imports = None):
		'''
		Creates and Agent instance and attemps to connect
		to the AgentMaster.  If connection works the Client Hello message
		is sent.
		
		@type	agentUri: string
		@param	agentUri: Url of agent
		@type	password: string
		@param	password: [optional] Password to authenticate to agent.  Warning: CLEAR-TEXT!!
		@type	pythonPaths: list
		@param	pythonPaths: List of paths we should configure on the remote agent
		@type	imports: list
		@param	imports: list of imports that should be performed on the remote agent
		'''
		
		self._pythonPaths = pythonPaths
		self._imports = imports
		self._password = password
		self._monitors = []
		self._id = None
		self._agent = None
		self._agentUri = agentUri
		
		if agentUri == "LocalAgent":
			# Swan up our own agent instance!
			agentUri = self._agentUri = "http://127.0.0.1:9000"
			
			# Only Windows on windows, this covers both 32bit & 64bit			
			if sys.platform == "win32":
				if self.main_is_frozen():
					# We are in py2exe
					#subprocess.call("start \"Local Peach Agent\" \"%s\" -a" % (sys.argv[0]), shell=True)
					self.LaunchWin32Process("cmd.exe /c \"start \"Local Peach Agent\"  \"%s\" -a\"" % (sys.argv[0]))
					
				else:
					# Figure out were Peach is!
					peachPath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
					#subprocess.call("start \"Local Peach Agent\" \"%s\" \"%s\\peach.py\" -a" %
					#	(sys.executable, peachPath), shell=True)
					self.LaunchWin32Process("cmd.exe /c \"start \"Local Peach Agent\" \"%s\" \"%s\\peach.py\" -a\"" %
						(sys.executable, peachPath))
					
			else:
				raise PeachException("Sorry, we only support auto starting agents on Windows.  Please configure all agents with location uris and pre-launch any Agent processes.")
			
		# Connect to remote agent
		try:
			m = re.search(r"://([^/]*)", agentUri)
			self._name = m.group(1)
		except:
			raise PeachException("Please make sure your agent location string is a valid http URL.")
		
		self.Connect()
		
	def LaunchWin32Process(self, command):
		try:
			StartupInfo = win32process.STARTUPINFO()
			StartupInfo.dwFlags = win32process.STARTF_USESHOWWINDOW
			StartupInfo.wShowWindow = win32con.SW_NORMAL
			win32process.CreateProcess(
				None,
				command,
				None,
				None,
				0,
				win32process.NORMAL_PRIORITY_CLASS,
				None,
				None,
				StartupInfo)
		except:
			print sys.exc_info()
			print "Exception in LaunchWin32Process"
			pass
	
	def main_is_frozen(self):
		return (hasattr(sys, "frozen") or # new py2exe
			hasattr(sys, "importers") # old py2exe
			or imp.is_frozen("__main__")) # tools/freeze

	def get_main_dir(self):
		if main_is_frozen():
			return os.path.dirname(sys.executable)
		return os.path.dirname(sys.argv[0])
	
	def Connect(self):
		'''
		Connect to agent.  Will retry the connection 10 times before
		giving up.
		'''
		
		for i in range(10):
			try:
				self._agent = ServerProxy(self._agentUri)
				
				msg = _Msg(None, _MsgType.ClientHello, self._name)
				msg.password = self._password
				msg.pythonPaths = self._pythonPaths
				msg.imports = self._imports
				
				msg = pickle.loads(self._agent.clientHello(pickle.dumps(msg)))
				
				if msg.type != _MsgType.AgentHello:
					raise PeachException("Error connecting to remote agent %s, invalid response." % self._name)
				
				self._id = msg.id
				return
				
			except:
				if i == 9:
					raise
			
			time.sleep(1)
			print "-- Agent connection failed, retrying..."
	
	def Reconnect(self):
		'''
		Reconnect to remote agent
		'''
		
		try:
			self.Connect()
			for m in self._monitors:
				self.StartMonitor(m[0], m[1], m[2], True)
			
		except:
			raise PeachException("Unable to reconnect to Agent %s." % self._name)
		
	def StartMonitor(self, name, classStr, params, restarting = False):
		
		Debug("> StartMonitor")
		
		msg = _Msg(self._id, _MsgType.StartMonitor)
		msg.monitorName = name
		msg.monitorClass = classStr
		msg.params = params
		
		msg = pickle.loads(self._agent.startMonitor(pickle.dumps(msg)))
		
		if msg.type != _MsgType.Ack:
			raise PeachException("Lost connection to Agent %s during StartMonitor call." % self._name)
		
		if not restarting:
			self._monitors.append([name, classStr, params])
			
		Debug("< StartMonitor")
	
	def StopMonitor(self, name):
		Debug("> StopMonitor")
		
		msg = _Msg(self._id, _MsgType.StopMonitor)
		msg.monitorName = name
		
		msg = pickle.loads(self._agent.stopMonitor(pickle.dumps(msg)))
		
		if msg.type != _MsgType.Ack:
			raise PeachException("Lost connection to Agent %s during StopMonitor call." % self._name)
		
		for m in self._monitors:
			if m[0] == name:
				self._monitors.remove(m)
		
		Debug("< StopMonitor")
	
	def OnTestStarting(self):
		'''
		Called right before start of test.
		'''
		
		Debug("> OnTestStarting")
		
		msg = _Msg(self._id, _MsgType.OnTestStarting)
		
		try:
			msg = pickle.loads(self._agent.onTestStarting(pickle.dumps(msg)))
		
		except:
			self.Reconnect()
			raise RedoTestException("Communication error with Agent %s" % self._name)
		
		if msg.type != _MsgType.Ack:
			raise PeachException("Lost connection to Agent %s during OnTestStarting call." % self._name)
		
		Debug("< OnTestStarting")
	
	def OnPublisherCall(self, method):
		Debug("> OnPublisherCall")
		
		msg = _Msg(self._id, _MsgType.PublisherCall)
		msg.method = method
		
		try:
			msg = pickle.loads(self._agent.onPublisherCall(pickle.dumps(msg)))
		
		except:
			self.Reconnect()
			raise RedoTestException("Communication error with Agent %s" % self._name)
		
		if msg.type != _MsgType.Ack:
			raise PeachException("Lost connection to Agent %s during OnPublisherCall call." % self._name)
		
		Debug("< OnPublisherCall")
		return msg.results
	
	def OnTestFinished(self):
		'''
		Called right after a test.
		'''
		
		Debug("> OnTestFinished")
		
		msg = _Msg(self._id, _MsgType.OnTestFinished)
		
		try:
			msg = pickle.loads(self._agent.onTestFinished(pickle.dumps(msg)))
			
		except:
			self.Reconnect()
			raise RedoTestException("Communication error with Agent %s" % self._name)
		
		if msg.type != _MsgType.Ack:
			raise PeachException("Lost connection to Agent %s during OnTestFinished call." % self._name)
		
		Debug("< OnTestFinished")

	def GetMonitorData(self):
		'''
		Get any monitored data.
		'''
		
		Debug("> GetMonitorData")
		
		msg = _Msg(self._id, _MsgType.GetMonitorData)
		
		try:
			msg = pickle.loads(self._agent.getMonitorData(pickle.dumps(msg)))
			
		except:
			self.Reconnect()
			raise RedoTestException("Communication error with Agent %s" % self._name)
		
		if msg.type != _MsgType.Ack:
			raise PeachException("Lost connection to Agent %s during GetMonitorData call." % self._name)
		
		Debug("< GetMonitorData")
		
		return msg.results
	
	def RedoTest(self):
		'''
		SHould we repeat current test
		'''
		
		Debug("> RedoTest")
		
		try:
			msg = _Msg(self._id, _MsgType.RedoTest)
			msg = pickle.loads(self._agent.redoTest(pickle.dumps(msg)))
			
		except:
			self.Reconnect()
			raise RedoTestException("Communication error with Agent %s" % self._name)
		
		if msg.type != _MsgType.Ack:
			raise PeachException("Lost connection to Agent %s during RedoTest call." % self._name)
		
		Debug("< RedoTest")
		
		return msg.results
	
	def DetectedFault(self):
		'''
		Check if a fault was detected.
		'''
		
		Debug("> DetectedFault")
		
		try:
			msg = _Msg(self._id, _MsgType.DetectFault)
			msg = pickle.loads(self._agent.detectFault(pickle.dumps(msg)))
			
		except:
			self.Reconnect()
			raise RedoTestException("Communication error with Agent %s" % self._name)
		
		if msg.type != _MsgType.Ack:
			raise PeachException("Lost connection to Agent %s during GetMonitorData call." % self._name)
		
		Debug("< DetectedFault")
		
		return msg.results
	
	def OnFault(self):
		'''
		Called when a fault was detected.
		'''
		
		Debug("> OnFault")
		
		try:
			msg = _Msg(self._id, _MsgType.OnFault)
			msg = pickle.loads(self._agent.onFault(pickle.dumps(msg)))
			
		except:
			self.Reconnect()
			raise RedoTestException("Communication error with Agent %s" % self._name)
		
		if msg.type != _MsgType.Ack:
			raise PeachException("Lost connection to Agent %s during GetMonitorData call." % self._name)
		
		Debug("< OnFault")
	
	def OnShutdown(self):
		'''
		Called when Agent is shutting down.
		'''
		
		Debug("> OnShutdown")
		
		msg = _Msg(self._id, _MsgType.OnShutdown)
		self._agent.onShutdown(pickle.dumps(msg))
		
		Debug("< OnShutdown")
	
	def StopRun(self):
		'''
		Return True to force test run to fail.  This
		should return True if an unrecoverable error
		occurs.
		'''
		
		Debug("> StopRun")
		
		try:
			msg = _Msg(self._id, _MsgType.StopRun)
			msg = pickle.loads(self._agent.stopRun(pickle.dumps(msg)))
			
		except:
			self.Reconnect()
			raise RedoTestException("Communication error with Agent %s" % self._name)
		
		if msg.type != _MsgType.Ack:
			raise PeachException("Lost connection to Agent %s during GetMonitorData call." % self._name)
		
		Debug("< StopRun")
		
		return msg.results
	
	## Publishers
	
	def PublisherInitialize(self, name, cls, args):
		ret = self._agent.publisherInitialize(self._id, name, cls, args)
		if ret != None and ret < 0:
			raise Exception("That sucked")
	
	def PublisherStart(self, name):
		ret = self._agent.publisherStart(self._id, name)
		if ret < 0:
			raise Exception("That sucked")
	
	def PublisherStop(self, name):
		ret = self._agent.publisherStop(self._id, name)
		if ret < 0:
			raise Exception("That sucked")
	
	def PublisherAccept(self, name):
		ret = self._agent.publisherAccept(self._id, name)
		if ret < 0:
			raise Exception("That sucked")
	
	def PublisherConnect(self, name):
		ret = self._agent.publisherConnect(self._id, name)
		if ret < 0:
			raise Exception("That sucked")
	
	def PublisherClose(self, name):
		ret = self._agent.publisherClose(self._id, name)
		if ret < 0:
			raise Exception("That sucked")
	
	def PublisherCall(self, name, method, args):
		ret = self._agent.publisherCall(self._id, name, method, pickle.dumps(args))
		if ret < 0:
			raise Exception("That sucked")
		
		return ret
	
	def PublisherProperty(self, name, property, value = None):
		ret = self._agent.publisherProperty(self._id, name, property, pickle.dumps(value))
		if ret < 0:
			raise Exception("That sucked")
		
		return ret
	
	def PublisherSend(self, name, data):
		ret = self._agent.publisherSend(self._id, name, pickle.dumps(data))
		if ret < 0:
			raise Exception("That sucked")
		
		return ret
	
	def PublisherReceive(self, name, size = None):
		ret = self._agent.publisherReceive(self._id, name, size)
		if ret < 0:
			raise Exception("That sucked")
		
		return ret


class AgentPlexer:
	'''
	Will manage communication with one or more agent.
	'''
	
	def __init__(self):
		self._agents = {}
	
	def __getitem__(self, key):
		return self._agents[key]
	def __setitem__(self, key, value):
		self._agents[key] = value
	
	def AddAgent(self, name, agentUri, password = None, pythonPath = None, imports = None):
		#m = re.search(r"://([^:/]*)", agentUri)
		#name = m.group(1)
		
		agent = AgentClient(agentUri, password, pythonPath, imports)
		self._agents[name] = agent
		return agent
	
	def OnTestStarting(self):
		'''
		Called right before start of test.
		'''
		for name in self._agents.keys():
			self._agents[name].OnTestStarting()
	
	def OnPublisherCall(self, method):
		ourRet = None
		for name in self._agents.keys():
			ret = self._agents[name].OnPublisherCall(method)
			if ret != None:
				ourRet = ret
		
		return ourRet
			
	def OnTestFinished(self):
		'''
		Called right after a test.
		'''
		for name in self._agents.keys():
			self._agents[name].OnTestFinished()
	
	def GetMonitorData(self):
		'''
		Get any monitored data.
		'''
		ret = {}
		for name in self._agents.keys():
			arrayOfMonitorData = self._agents[name].GetMonitorData()
			
			for hashOfData in arrayOfMonitorData:
				for key in hashOfData.keys():
					#print "Creating key: [%s]" % ( "%s_%s" % (name, key))
					ret["%s_%s" % (name, key)] = hashOfData[key]
		
		return ret
	
	def RedoTest(self):
		'''
		Check if a fault was detected.
		'''
		ret = False
		for name in self._agents.keys():
			if self._agents[name].RedoTest():
				ret = True
		
		return ret
	
	def DetectedFault(self):
		'''
		Check if a fault was detected.
		'''
		ret = False
		for name in self._agents.keys():
			if self._agents[name].DetectedFault():
				ret = True
		
		return ret
	
	def OnFault(self):
		'''
		Called when a fault was detected.
		'''
		for name in self._agents.keys():
			self._agents[name].OnFault()
	
	def OnShutdown(self):
		'''
		Called when Agent is shutting down.
		'''
		for name in self._agents.keys():
			self._agents[name].OnShutdown()
		
		self._agents = {}
	
	def StopRun(self):
		'''
		Return True to force test run to fail.  This
		should return True if an unrecoverable error
		occurs.
		'''
		
		ret = False
		for name in self._agents.keys():
			if self._agents[name].StopRun():
				ret = True
			
		return ret
	
	## Publishers
	
	def PublisherInitialize(self, name, cls, args):
		for name in self._agents.keys():
			self._agents[name].PublisherInitialize(name, cls, args)
	
	def PublisherStart(self, name):
		for name in self._agents.keys():
			self._agents[name].PublisherStart(name)
	
	def PublisherStop(self, name):
		for name in self._agents.keys():
			self._agents[name].PublisherStop(name)
	
	def PublisherAccept(self, name):
		for name in self._agents.keys():
			self._agents[name].PublisherAccept(name)
	
	def PublisherConnect(self, name):
		for name in self._agents.keys():
			self._agents[name].PublisherConnect(name)
	
	def PublisherClose(self, name):
		for name in self._agents.keys():
			self._agents[name].PublisherClose(name)
	
	def PublisherCall(self, name, method, args):
		for name in self._agents.keys():
			self._agents[name].PublisherCall(name, method, args)
			if ret != None:
				return ret
		
		return None
	
	def PublisherProperty(self, name, property, value = None):
		for name in self._agents.keys():
			ret = self._agents[name].PublisherProperty(name, property, value)
			if ret != None:
				return ret
		
		return None
	
	def PublisherSend(self, name, data):
		for name in self._agents.keys():
			self._agents[name].PublisherSend(name, data)
	
	def PublisherReceive(self, name, size = None):
		for name in self._agents.keys():
			self._agents[name].PublisherReceive(name, size)
			if ret != None:
				return ret
		
		return None

# end
