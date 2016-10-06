
'''
Process control agent.  This agent is able to start, stop, and monitor
if a process is running.  If the process exits early a fault will be
issued to the fuzzer.

@author: Michael Eddington
@version: $Id: process.py 2571 2011-10-31 23:22:24Z meddingt $
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

# $Id: process.py 2571 2011-10-31 23:22:24Z meddingt $

import sys, time
import os

try:
	import win32con
	from win32process import *
except:
	# Only complain on Windows platforms.
	if sys.platform == 'win32':
		print "Warning: win32 extensions not found, disabing variouse process monitors."

from Peach.agent import Monitor

class PageHeap(Monitor):
	'''
	A monitor that will enable/disable pageheap on an executable.
	'''
	
	def __init__(self, args):
		'''
		Params: Path, Executable
		'''
		
		try:
			self._path = os.path.join(args['Path'].replace("'''", ""), "gflags.exe")
			
		except:
			self._path = os.path.join(self.LocateWinDbg(), 'gflags.exe')
		
		self._exe = args['Executable'].replace("'''", "")
		
		self._onParams = [ 'gflags.exe', '/p', '/full', '/enable', self._exe ]
		self._offParams = [ 'gflags.exe', '/p', '/disable', self._exe ]
		
		try:
			os.spawnv(os.P_WAIT, self._path, self._onParams )
		except:
			print "Error, PageHeap failed to launch:"
			print "\tself._path:", self._path
			print "\tself._onParams", self._onParams
			raise
	
	def LocateWinDbg(self):
		'''
		NOTE: Update master copy in debugger.py if you change this!!!!
		'''
		
		import win32api, win32con
		try:
			hkey = win32api.RegOpenKey(win32con.HKEY_CURRENT_USER, "Software\\Microsoft\\DebuggingTools")
			val, type = win32api.RegQueryValueEx(hkey, "WinDbg")
			return val
		except:
			
			# Lets try a few common places before failing.
			pgPaths = [
				"c:\\",
				os.environ["SystemDrive"]+"\\",
				os.environ["ProgramFiles"],
				]
			if "ProgramW6432" in os.environ:
				pgPaths.append(os.environ["ProgramW6432"])
			if "ProgramFiles(x86)" in os.environ:
				pgPaths.append(os.environ["ProgramFiles(x86)"])
			
			dbgPaths = [
				"Debuggers",
				"Debugger",
				"Debugging Tools for Windows",
				"Debugging Tools for Windows (x64)",
				"Debugging Tools for Windows (x86)",
				]
			
			for p in pgPaths:
				for d in dbgPaths:
					testPath = os.path.join(p,d)
					
					if os.path.exists(testPath):
						return testPath
		
		print "!!! Unable to locate gflags.exe !!!"
			
		
	def OnShutdown(self):
		os.spawnv(os.P_WAIT, self._path, self._offParams )


class WindowsProcess(Monitor):
	'''
	Process control agent.  This agent is able to start, stop, and monitor
	if a process is running.  If the process exits early a fault will be
	issued to the fuzzer.
	'''
	
	def __init__(self, args):
		self.restartOnTest = False
		if args.has_key('RestartOnEachTest'):
			if args['RestartOnEachTest'].replace("'''", "").lower() == 'true':
				self.restartOnTest = True
		
		self.faultOnEarlyExit = True
		if args.has_key('FaultOnEarlyExit'):
			if args['FaultOnEarlyExit'].replace("'''", "").lower() != 'true':
				self.faultOnEarlyExit = False
		
		self.startOnCall = False
		if args.has_key('StartOnCall'):
			self.startOnCall = True
			self.startOnCallMethod = args['StartOnCall'].replace("'''", "").lower()
		
		self.waitForExitOnCall = False
		if args.has_key('WaitForExitOnCall'):
			self.waitForExitOnCall = True
			self.waitForExitOnCallMethod = args['WaitForExitOnCall'].replace("'''", "").lower()
		
		if not args.has_key('Command'):
			raise PeachException("Error, monitor Process requires a parameter named 'Command'")
		
		self.strangeExit = False
		self.command = args["Command"].replace("'''", "")
		self.args = None
		self.pid = None
		self.hProcess = None
		self.hThread = None
		self.dwProcessId = None
		self.dwThreadId = None
	
	def PublisherCall(self, method):
		
		method = method.lower()
		if self.startOnCall and self.startOnCallMethod == method:
			print "Process: startOnCall, starting process!"
			
			self._StopProcess()
			self._StartProcess()
		
		elif self.waitForExitOnCall and self.waitForExitOnCallMethod == method:
			print "Process: waitForExitOnCall, waiting on process exit"
			
			while True:
				if not self._IsProcessRunning:
					print "Process: Process exitted"
					return
				time.sleep(0.25)
	
	def _StopProcess(self):
		
		if self.hProcess == None:
			return
		
		if self._IsProcessRunning():
			TerminateProcess(self.hProcess, 0)
		
		self.hProcess = None
		self.hThread = None
		self.dwProcessId = None
		self.dwThreadId = None
	
	def _StartProcess(self):
		if self.hProcess != None:
			self._StopProcess()
		
		(hProcess, hThread, dwProcessId, dwThreadId) = CreateProcess(None, self.command,
			None, None, 0, 0, None, None, STARTUPINFO())
		
		self.hProcess = hProcess
		self.hThread = hThread
		self.dwProcessId = dwProcessId
		self.dwThreadId = dwThreadId
	
	def _IsProcessRunning(self):
		if self.hProcess == None:
			return False
		
		ret = GetExitCodeProcess(self.hProcess)
		if ret != win32con.STILL_ACTIVE:
			return False
		
		ret = GetExitCodeThread(self.hThread)
		if ret != win32con.STILL_ACTIVE:
			return False
		
		return True
	
	def OnTestStarting(self):
		'''
		Called right before start of test.
		'''
		self.strangeExit = False
		if not self.startOnCall and (self.restartOnTest or not self._IsProcessRunning()):
			self._StopProcess()
			self._StartProcess()
		elif self.startOnCall:
			self._StopProcess()
	
	def OnTestFinished(self):
		'''
		Called right after a test.
		'''
		if not self._IsProcessRunning():
			self.strangeExit = True
			
		if self.restartOnTest:
			self._StopProcess()
	
		elif self.startOnCall:
			self._StopProcess()
	
	def GetMonitorData(self):
		'''
		Get any monitored data.
		'''
		if self.strangeExit:
			return { "WindowsProcess.txt" : "Process exited early" }
		
		return None
	
	def DetectedFault(self):
		'''
		Check if a fault was detected.  If the process exits
		with out our help we will report it as a fault.
		'''
		if self.faultOnEarlyExit:
			return not self._IsProcessRunning()
		
		else:
			return False
	
	def OnFault(self):
		'''
		Called when a fault was detected.
		'''
		self._StopProcess()
	
	def OnShutdown(self):
		'''
		Called when Agent is shutting down.
		'''
		self._StopProcess()

from subprocess import *
import signal, os

class Process(Monitor):
	'''
	Process control agent.  This agent is able to start, stop, and monitor
	if a process is running.  If the process exits early a fault will be
	issued to the fuzzer.
	'''
	
	def __init__(self, args):
		self.restartOnTest = False
		if args.has_key('RestartOnEachTest'):
			if args['RestartOnEachTest'].replace("'''", "").lower() == 'true':
				self.restartOnTest = True
		
		self.faultOnEarlyExit = True
		if args.has_key('FaultOnEarlyExit'):
			if args['FaultOnEarlyExit'].replace("'''", "").lower() != 'true':
				self.faultOnEarlyExit = False
		
		self.startOnCall = False
		if args.has_key('StartOnCall'):
			self.startOnCall = True
			self.startOnCallMethod = args['StartOnCall'].replace("'''", "").lower()
		
		self.waitForExitOnCall = False
		if args.has_key('WaitForExitOnCall'):
			self.waitForExitOnCall = True
			self.waitForExitOnCallMethod = args['WaitForExitOnCall'].replace("'''", "").lower()
		
		if not args.has_key('Command'):
			raise PeachException("Error, monitor Process requires a parameter named 'Command'")
		
		self.strangeExit = False
		self.command = args["Command"].replace("'''", "")
		self.args = self.command.split()
		self.pid = None
		self.process = None
	
	def PublisherCall(self, method):
		
		method = method.lower()
		if self.startOnCall and self.startOnCallMethod == method:
			print "Process: startOnCall, starting process!"
			
			self._StopProcess()
			self._StartProcess()
		
		elif self.waitForExitOnCall and self.waitForExitOnCallMethod == method:
			print "Process: waitForExitOnCall, waiting on process exit"
			
			while True:
				if not self._IsProcessRunning():
					print "Process: Process exitted"
					return
				time.sleep(0.25)
	
	def _StopProcess(self):
		
		print "Process._StopProcess"
		
		if not self.process:
			return
		
		if self._IsProcessRunning():
			try:
				os.kill(self.process.pid, signal.SIGTERM)
				os.kill(self.process.pid, signal.SIGKILL)
			except:
				pass
			self.process.wait()
		
		self.process = None
	
	def _StartProcess(self):
		
		print "Process._StartProcess"
		
		if self.process:
			self._StopProcess()
		
		self.process = Popen(self.args)
	
	def _IsProcessRunning(self):
		
		if self.process == None:
			print "Process._IsProcessRunning: False (self.process == None)"
			return False
		
		if self.process.poll() != None:
			print "Process._IsProcessRunning: False (self.process.poll != None)"
			return False
		
		print "Process._IsProcessRunning: True"
		return True
	
	def OnTestStarting(self):
		'''
		Called right before start of test.
		'''
		self.strangeExit = False
		if not self.startOnCall and (self.restartOnTest or not self._IsProcessRunning()):
			print "Process.OnTestStarting: Stopping and starting process"
			self._StopProcess()
			self._StartProcess()
			
		elif self.startOnCall:
			print "Process.OnTestStarting: Stopping process"
			self._StopProcess()
		
		print "Exiting OnTestStarting..."
	
	def OnTestFinished(self):
		'''
		Called right after a test.
		'''
		if not self._IsProcessRunning():
			self.strangeExit = True
			
		if self.restartOnTest:
			print "Process.OnTestFinished: Stopping process"
			self._StopProcess()
	
		elif self.startOnCall:
			print "Process.OnTestFinished: Stopping process"
			self._StopProcess()
	
	def GetMonitorData(self):
		'''
		Get any monitored data.
		'''
		if self.strangeExit:
			return {"Process.txt" : "Process exited early"}
		
		return None
	
	def DetectedFault(self):
		'''
		Check if a fault was detected.  If the process exits
		with out our help we will report it as a fault.
		'''
		if self.faultOnEarlyExit:
			return self.strangeExit
		
		else:
			return False
	
	def OnFault(self):
		'''
		Called when a fault was detected.
		'''
		self._StopProcess()
	
	def OnShutdown(self):
		'''
		Called when Agent is shutting down.
		'''
		self._StopProcess()

try:
	import win32serviceutil
except:
	pass

class WindowsService(Monitor):
	'''
	Controls a windows service making sure it's started,
	optionally restarting, etc.
	'''
	
	def __init__(self, args):
		if args.has_key('RestartOnEachTest'):
			if args['RestartOnEachTest'].lower() == 'true':
				self.restartOnTest = True
			else:
				self.restartOnTest = False
		else:
			self.restartOnTest = False
		
		if args.has_key('FaultOnEarlyExit'):
			if args['FaultOnEarlyExit'].lower() == 'true':
				self.faultOnEarlyExit = True
			else:
				self.faultOnEarlyExit = False
		else:
			self.faultOnEarlyExit = True
		
		self.strangeExit = False
		self.service = args["Service"].replace("'''", "")
		
		if args.has_key("Machine"):
			self.machine = args["Machine"].replace("'''", "")
		else:
			self.machine = None
	
	def _StopProcess(self):
		win32serviceutil.StopService(self.service, self.machine)
		
		while win32serviceutil.QueryServiceStatus(self.service, self.machine)[1] == 3:
			time.sleep(0.25)
		
		if win32serviceutil.QueryServiceStatus(self.service, self.machine)[1] != 1:
			raise Exception("WindowsService: Unable to stop service!")
	
	def _StartProcess(self):
		if self._IsProcessRunning():
			return
		
		win32serviceutil.StartService(self.service, self.machine)
		
		while win32serviceutil.QueryServiceStatus(self.service, self.machine)[1] == 2:
			time.sleep(0.25)
			
		if win32serviceutil.QueryServiceStatus(self.service, self.machine)[1] == 4:
			raise Exception("WindowsService: Unable to start service!")
		
	def _IsProcessRunning(self):
		if win32serviceutil.QueryServiceStatus(self.service, self.machine)[1] == 4:
			return True
		
		return False
	
	def OnTestStarting(self):
		'''
		Called right before start of test.
		'''
		self.strangeExit = False
		if self.restartOnTest or not self._IsProcessRunning():
			self._StopProcess()
			self._StartProcess()
	
	def OnTestFinished(self):
		'''
		Called right after a test.
		'''
		if not self._IsProcessRunning():
			self.strangeExit = True
		
		if self.restartOnTest:
			self._StopProcess()
	
	def GetMonitorData(self):
		'''
		Get any monitored data.
		'''
		if self.strangeExit:
			return {"WindowsService.txt" : "Process exited early"}
		
		return None
	
	def DetectedFault(self):
		'''
		Check if a fault was detected.  If the process exits
		with out our help we will report it as a fault.
		'''
		#if self.faultOnEarlyExit:
		#	return not self._IsProcessRunning()
		#
		#else:
		#	return False
		return False
	
	def OnFault(self):
		'''
		Called when a fault was detected.
		'''
		self._StopProcess()
	
	def OnShutdown(self):
		'''
		Called when Agent is shutting down.
		'''
		#self._StopProcess()
		pass

try:

	import win32gui, win32con
	import sys,time, os, signal
	from threading import *
	from Peach.agent import *
except:
	pass

class ProcessKiller(Monitor):
	''' Will watch for specific process and kill '''
	
	def __init__(self, args):
		'''
		Constructor.  Arguments are supplied via the Peach XML
		file.
		
		@type    args: Dictionary
		@param    args: Dictionary of parameters
		'''
		
		# Our name for this monitor
		self._name = "ProcessWatcher"
		
		if not args.has_key("ProcessNames"):
			raise Exception("ProcessWatcher requires a parameter named ProcessNames.")
		
		self._names = args["ProcessNames"].replace("'''", "").split(',')
	
	def OnTestStarting(self):
		'''
		Called right before start of test case or variation
		'''
		pass
	
	def OnTestFinished(self):
		'''
		Called right after a test case or varation
		'''
		for name in self._names:
			os.popen('TASKKILL /IM ' + name + ' /F')
			time.sleep(.6)
	
	def DetectedFault(self):
		'''
		Check if a fault was detected.
		'''
		return False
	
	def OnShutdown(self):
		'''
		Called when Agent is shutting down, typically at end
		of a test run or when a Stop-Run occurs
		'''
		try:
			for name in self._names:
				os.popen('TASKKILL /IM ' + name + ' /F')
				time.sleep(.6)
		except:
			pass

# end
