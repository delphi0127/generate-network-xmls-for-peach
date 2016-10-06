
'''
Take a crashing file and the origional sample.  Locate the minimum change
required to cause crash.
'''

import struct, sys, time, os, re, pickle
import gc, tempfile
from multiprocessing import *

try:
	
	import comtypes
	from ctypes import *
	from comtypes import HRESULT, COMError
	from comtypes.client import CreateObject, GetEvents, PumpEvents
	from comtypes.hresult import S_OK, E_FAIL, E_UNEXPECTED, E_INVALIDARG
	from comtypes.automation import IID
	import PyDbgEng
	from comtypes.gen import DbgEng
	import win32serviceutil
	import win32service
	import win32api, win32con, win32process, win32pdh
	
	
	# ###############################################################################################
	# ###############################################################################################
	# ###############################################################################################
	# ###############################################################################################
	
	class _DbgEventHandler(PyDbgEng.IDebugOutputCallbacksSink, PyDbgEng.IDebugEventCallbacksSink):
		
		buff = ''
		
		def LocateWinDbg(self):
			'''
			This method also exists in process.PageHeap!
			'''
			
			try:
				
				hkey = win32api.RegOpenKey(win32con.HKEY_CURRENT_USER, "Software\\Microsoft\\DebuggingTools")
			
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
				
				return None
			
			val, type = win32api.RegQueryValueEx(hkey, "WinDbg")
			win32api.RegCloseKey(hkey)
			return val
		
		def Output(self, this, Mask, Text):
			self.buff += Text
			
		def LoadModule(self, unknown, imageFileHandle, baseOffset, moduleSize, moduleName, imageName, checkSum, timeDateStamp = None):
			if self.pid == None:
				self.dbg.idebug_control.Execute(DbgEng.DEBUG_OUTCTL_THIS_CLIENT,
										   c_char_p("|."),
										   DbgEng.DEBUG_EXECUTE_ECHO)
				
				match = re.search(r"\.\s+\d+\s+id:\s+([0-9a-fA-F]+)\s+\w+\s+name:\s", self.buff)
				if match != None:
					self.pid = int(match.group(1), 16)
					
					# Write out PID for main peach process
					fd = open(self.TempfilePid, "wb+")
					fd.write(str(self.pid))
					fd.close()
		
		def GetInterestMask(self):
			return PyDbgEng.DbgEng.DEBUG_EVENT_EXCEPTION | PyDbgEng.DbgEng.DEBUG_FILTER_INITIAL_BREAKPOINT | \
				PyDbgEng.DbgEng.DEBUG_EVENT_EXIT_PROCESS | PyDbgEng.DbgEng.DEBUG_EVENT_LOAD_MODULE
		
		def ExitProcess(self, dbg, ExitCode):
			print "_DbgEventHandler.ExitProcess: Target application has exitted"
			self.quit.set()
			return DEBUG_STATUS_NO_CHANGE
		
		def Exception(self, dbg, ExceptionCode, ExceptionFlags, ExceptionRecord,
				ExceptionAddress, NumberParameters, ExceptionInformation0, ExceptionInformation1,
				ExceptionInformation2, ExceptionInformation3, ExceptionInformation4,
				ExceptionInformation5, ExceptionInformation6, ExceptionInformation7,
				ExceptionInformation8, ExceptionInformation9, ExceptionInformation10,
				ExceptionInformation11, ExceptionInformation12, ExceptionInformation13,
				ExceptionInformation14, FirstChance):
			
			if self.IgnoreSecondChanceGardPage and ExceptionCode == 0x80000001:
				return DbgEng.DEBUG_STATUS_NO_CHANGE
			
			# Only capture dangerouse first chance exceptions
			if FirstChance:
				if self.IgnoreFirstChanceGardPage and ExceptionCode == 0x80000001:
					# Ignore, sometimes used as anti-debugger
					# by Adobe Flash.
					return DbgEng.DEBUG_STATUS_NO_CHANGE
				
				# Guard page or illegal op
				elif ExceptionCode == 0x80000001 or ExceptionCode == 0xC000001D:
					pass
				elif ExceptionCode == 0xC0000005:
					# is av on eip?
					if ExceptionInformation0 == 0 and ExceptionInformation1 == ExceptionAddress:
						pass
					
					# is write a/v?
					elif ExceptionInformation0 == 1 and ExceptionInformation1 != 0:
						pass
					
					# is DEP?
					elif ExceptionInformation0 == 0:
						pass
					
					else:
						# Otherwise skip first chance
						return DbgEng.DEBUG_STATUS_NO_CHANGE
				else:
					# otherwise skip first chance
					return DbgEng.DEBUG_STATUS_NO_CHANGE
					
			
			if self.handlingFault.is_set() or self.handledFault.is_set():
				# We are already handling, so skip
				#sys.stdout.write("_DbgEventHandler::Exception(): handlingFault set, skipping.\n")
				return DbgEng.DEBUG_STATUS_BREAK
			
			#print "Exception: Found interesting exception"
			
			self.crashInfo = {"wecrash":"bigtime!"}
			self.handlingFault.set()
			
			self.buff = ""
			self.fault = True
			
			fd = open(self.Tempfile, "wb+")
			fd.write(pickle.dumps(self.crashInfo))
			fd.close()
			
			self.handledFault.set()
			return DbgEng.DEBUG_STATUS_BREAK


	def WindowsDebugEngineProcess_run(*args, **kwargs):
		
		started = kwargs['Started']
		handlingFault = kwargs['HandlingFault']
		handledFault = kwargs['HandledFault']
		CommandLine = kwargs.get('CommandLine', None)
		Service = kwargs.get('Service', None)
		ProcessName = kwargs.get('ProcessName', None)
		ProcessID = kwargs.get('ProcessID', None)
		KernelConnectionString = kwargs.get('KernelConnectionString', None)
		SymbolsPath = kwargs.get('SymbolsPath', None)
		IgnoreFirstChanceGardPage = kwargs.get('IgnoreFirstChanceGardPage', None)
		IgnoreSecondChanceGardPage = kwargs.get('IgnoreSecondChanceGardPage', None)
		quit = kwargs['Quit']
		Tempfile = kwargs['Tempfile']
		TempfilePid = kwargs['TempfilePid']
		dbg = None
		
		# Hack for comtypes early version
		comtypes._ole32.CoInitializeEx(None, comtypes.COINIT_APARTMENTTHREADED)
		
		try:
			_eventHandler = _DbgEventHandler()
			_eventHandler.pid = None
			_eventHandler.handlingFault = handlingFault
			_eventHandler.handledFault = handledFault
			_eventHandler.IgnoreFirstChanceGardPage = IgnoreFirstChanceGardPage
			_eventHandler.IgnoreSecondChanceGardPage = IgnoreSecondChanceGardPage
			_eventHandler.quit = quit
			_eventHandler.Tempfile = Tempfile
			_eventHandler.TempfilePid = TempfilePid
			
			if KernelConnectionString:
				dbg = PyDbgEng.KernelAttacher(  connection_string = connection_string,
					follow_forks = True,
					event_callbacks_sink = _eventHandler,
					output_callbacks_sink = _eventHandler,
					symbols_path = SymbolsPath)
			
			elif CommandLine:
				dbg = PyDbgEng.ProcessCreator(command_line = CommandLine,
					follow_forks = True,
					event_callbacks_sink = _eventHandler,
					output_callbacks_sink = _eventHandler,
					symbols_path = SymbolsPath)
			
			elif ProcessName:
				
				pid = None
				for x in range(10):
					pid = GetProcessIdByName(ProcessName)
					if pid != None:
						break
					
					time.sleep(0.25)
				
				if pid == None:
					raise Exception("Error, unable to locate process '%s'" % ProcessName)
				
				dbg = PyDbgEng.ProcessAttacher(pid,
					event_callbacks_sink = _eventHandler,
					output_callbacks_sink = _eventHandler,
					symbols_path = SymbolsPath)
			
			elif ProcessID:
				
				pid = ProcessID
				dbg = PyDbgEng.ProcessAttacher(pid,	event_callbacks_sink = _eventHandler,
					output_callbacks_sink = _eventHandler, symbols_path = SymbolsPath)
				
			elif Service:
				
				# Make sure service is running
				if win32serviceutil.QueryServiceStatus(Service)[1] != 4:
					try:
						# Some services auto-restart, if they do
						# this call will fail.
						win32serviceutil.StartService(Service)
					except:
						pass
					
					while win32serviceutil.QueryServiceStatus(Service)[1] == 2:
						time.sleep(0.25)
						
					if win32serviceutil.QueryServiceStatus(Service)[1] != 4:
						raise Exception("WindowsDebugEngine: Unable to start service!")
				
				# Determin PID of service
				scm = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ALL_ACCESS)
				hservice = win32service.OpenService(scm, Service, 0xF01FF)
				
				status = win32service.QueryServiceStatusEx(hservice)
				pid = status["ProcessId"]
				
				win32service.CloseServiceHandle(hservice)
				win32service.CloseServiceHandle(scm)
				
				dbg = PyDbgEng.ProcessAttacher(pid,
					event_callbacks_sink = _eventHandler,
					output_callbacks_sink = _eventHandler,
					symbols_path = SymbolsPath)
			
			else:
				raise Exception("Didn't find way to start debugger... bye bye!!")
			
			_eventHandler.dbg = dbg
			started.set()
			dbg.event_loop_with_quit_event(quit)
			
		finally:
			if dbg != None:
				dbg.idebug_client.EndSession(DbgEng.DEBUG_END_ACTIVE_TERMINATE)
				dbg.idebug_client.Release()
			
			dbg = None
			
			comtypes._ole32.CoUninitialize()
	
	
	def GetProcessIdByName(procname):
		'''
		Try and get pid for a process by name.
		'''
		
		ourPid = -1
		procname = procname.lower()
		
		try:
			ourPid = win32api.GetCurrentProcessId()
		
		except:
			pass
		
		pids = win32process.EnumProcesses()
		for pid in pids:
			if ourPid == pid:
				continue
			
			try:
				hPid = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, 0, pid)
				
				try:
					mids = win32process.EnumProcessModules(hPid)
					for mid in mids:
						name = str(win32process.GetModuleFileNameEx(hPid, mid))
						if name.lower().find(procname) != -1:
							return pid
					
				finally:
					win32api.CloseHandle(hPid)
			except:
				pass
		
		return None
	
	class WindowsDebugEngine:
		def __init__(self, args):
			
			self.started = None
			# Set at start of exception handling
			self.handlingFault = None
			# Set when collection finished
			self.handledFault = None
			self.crashInfo = None
			self.fault = False
			self.thread = None
			self.tempfile = None
			
			if args.has_key('CommandLine'):
				self.CommandLine = str(args['CommandLine']).replace("'''", "")
			else:
				self.CommandLine = None
			
			if args.has_key('Service'):
				self.Service = str(args['Service']).replace("'''", "")
			else:
				self.Service = None
			
			if args.has_key('ProcessName'):
				self.ProcessName = str(args['ProcessName']).replace("'''", "")
			else:
				self.ProcessName = None
			
			if args.has_key('ProcessID'):
				self.ProcessID = int(args['ProcessID'].replace("'''", ""))
			else:
				self.ProcessID = None
			
			if args.has_key('KernelConnectionString'):
				self.KernelConnectionString = str(args['KernelConnectionString']).replace("'''", "")
			else:
				self.KernelConnectionString = None
			
			if args.has_key('SymbolsPath'):
				self.SymbolsPath = str(args['SymbolsPath']).replace("'''", "")
			else:
				self.SymbolsPath = "SRV*http://msdl.microsoft.com/download/symbols"
			
			if args.has_key("StartOnCall"):
				self.StartOnCall = True
				self.OnCallMethod = str(args['StartOnCall']).replace("'''", "").lower()
				
			else:
				self.StartOnCall = False
			
			if args.has_key("IgnoreFirstChanceGardPage"):
				self.IgnoreFirstChanceGardPage = True
			else:
				self.IgnoreFirstChanceGardPage = False
			
			if args.has_key("IgnoreSecondChanceGardPage"):
				self.IgnoreSecondChanceGardPage = True
			else:
				self.IgnoreSecondChanceGardPage = False
			
			if args.has_key("NoCpuKill"):
				self.NoCpuKill = True
			else:
				self.NoCpuKill = False
			
			if self.Service == None and self.CommandLine == None and self.ProcessName == None \
					and self.KernelConnectionString == None and self.ProcessID == None:
				raise PeachException("Unable to create WindowsDebugEngine, missing Service, or CommandLine, or ProcessName, or ProcessID, or KernelConnectionString parameter.")
			
		
		def _StartDebugger(self):
			
			try:
				if self.cpu_hq != None:
					win32pdh.RemoveCounter(self.cpu_counter_handle)
					win32pdh.CloseQuery(self.cpu_hq)
					self.cpu_hq = None
					self.cpu_counter_handle = None
			except:
				pass
			
			# Clear all our event handlers
			self.started = Event()
			self.quit = Event()
			self.handlingFault = Event()
			self.handledFault = Event()
			self.crashInfo = None
			self.fault = False
			self.pid = None
			self.cpu_process = None
			self.cpu_path = None
			self.cpu_hq = None
			self.cpu_counter_handle = None
			
			(fd, self.tempfile) = tempfile.mkstemp()
			os.close(fd)
			(fd, self.tempfilepid) = tempfile.mkstemp()
			os.close(fd)
			
			try:
				os.unlink(self.tempfile)
			except:
				pass
			
			self.thread = Process(group = None, target = WindowsDebugEngineProcess_run, kwargs = {
				'Started':self.started,
				'HandlingFault':self.handlingFault,
				'HandledFault':self.handledFault,
				'CommandLine':self.CommandLine,
				'Service':self.Service,
				'ProcessName':self.ProcessName,
				'ProcessID':self.ProcessID,
				'KernelConnectionString':self.KernelConnectionString,
				'SymbolsPath':self.SymbolsPath,
				'IgnoreFirstChanceGardPage':self.IgnoreFirstChanceGardPage,
				'IgnoreSecondChanceGardPage':self.IgnoreSecondChanceGardPage,
				'Quit':self.quit,
				'Tempfile':self.tempfile,
				'TempfilePid':self.tempfilepid
				})
			
			# Kick off our thread:
			self.thread.start()
			
			# Wait it...!
			self.started.wait()
		
		def _StopDebugger(self):
			try:
				if self.cpu_hq != None:
					win32pdh.RemoveCounter(self.cpu_counter_handle)
					win32pdh.CloseQuery(self.cpu_hq)
					self.cpu_hq = None
					self.cpu_counter_handle = None
			except:
				pass
			
			if self.thread != None and self.thread.is_alive():
				self.quit.set()
				self.started.clear()
				
				self.thread.join(5)
				
				if self.thread.is_alive():
					self.thread.terminate()
					self.thread.join()
				
				time.sleep(0.25) # Take a breath
			
			elif self.thread != None:
				# quit could be set by event handler now
				self.thread.join()
			
			self.thread = None
		
		def _IsDebuggerAlive(self):
			return self.thread and self.thread.is_alive()
		
		def OnTestStarting(self):
			if not self.StartOnCall and not self._IsDebuggerAlive():
				self._StartDebugger()
			elif self.StartOnCall:
				self._StopDebugger()
		
		def PublisherCall(self, method):
			
			if not self.StartOnCall:
				return None
			
			if self.OnCallMethod == method.lower():
				self._StartDebugger()
				return True
			
			if self.OnCallMethod+"_isrunning" == method.lower():
				if not self.quit.is_set():
					if self.pid == None:
						fd = open(self.tempfilepid, "rb+")
						pid = fd.read()
						fd.close()
						
						if len(pid) != 0:
							self.pid = int(pid)
							
							try:
								os.unlink(self.tempfilepid)
							except:
								pass
					
					if self.NoCpuKill == False and self.pid != None:
						# Check and see if the CPU utalization is low
						if self.cpu_process == None:
							self.cpu_process = self.getProcessInstance(self.pid)
						
						cpu = self.getProcessCpuTimeWindows(self.cpu_process)
						if cpu != None and cpu < 1.0:
							cpu = self.getProcessCpuTimeWindows(self.cpu_process)
							if cpu != None and cpu < 1.0 and not self.quit.is_set():
								self._StopDebugger()
								return False
				
				return not self.quit.is_set()
			
			return None
			
		def getProcessCpuTimeWindows(self, process):
			'''
			Get the current CPU processor time as a double based on a process
			instance (chrome#10).
			'''
			
			try:
				if process == None:
					return None
				
				if self.cpu_path == None:
					self.cpu_path = win32pdh.MakeCounterPath( (None, 'Process', process, None, 0, '% Processor Time') )
				
				if self.cpu_hq == None:
					self.cpu_hq = win32pdh.OpenQuery()
				
				if self.cpu_counter_handle == None:
					self.cpu_counter_handle = win32pdh.AddCounter(self.cpu_hq, self.cpu_path) #convert counter path to counter handle
					win32pdh.CollectQueryData(self.cpu_hq) #collects data for the counter
					time.sleep(0.25)
				
				win32pdh.CollectQueryData(self.cpu_hq) #collects data for the counter
				(v,cpu) = win32pdh.GetFormattedCounterValue(self.cpu_counter_handle, win32pdh.PDH_FMT_DOUBLE)
				return cpu
			
			except:
				print sys.exc_info()
			
			return None
		
		def getProcessInstance(self, pid):
			'''
			Get the process instance name using pid.
			'''
			
			hq = None
			counter_handle = None
			
			try:
				
				win32pdh.EnumObjects(None, None, win32pdh.PERF_DETAIL_WIZARD)
				junk, instances = win32pdh.EnumObjectItems(None,None,'Process', win32pdh.PERF_DETAIL_WIZARD)
			
				proc_dict = {}
				for instance in instances:
					if proc_dict.has_key(instance):
						proc_dict[instance] = proc_dict[instance] + 1
					else:
						proc_dict[instance]=0
				
				proc_ids = []
				for instance, max_instances in proc_dict.items():
					for inum in xrange(max_instances+1):
						hq = win32pdh.OpenQuery() # initializes the query handle 
						try:
							path = win32pdh.MakeCounterPath( (None, 'Process', instance, None, inum, 'ID Process') )
							counter_handle=win32pdh.AddCounter(hq, path) #convert counter path to counter handle
							try:
								win32pdh.CollectQueryData(hq) #collects data for the counter 
								type, val = win32pdh.GetFormattedCounterValue(counter_handle, win32pdh.PDH_FMT_LONG)
								proc_ids.append((instance, val))
								
								if val == pid:
									return "%s#%d" % (instance, inum)
								
							except win32pdh.error, e:
								#print e
								pass
							
							win32pdh.RemoveCounter(counter_handle)
							counter_handle = None
						
						except win32pdh.error, e:
							#print e
							pass
						win32pdh.CloseQuery(hq)
						hq = None
			except:
				print sys.exc_info()
			
			finally:
				
				try:
					if counter_handle != None:
						win32pdh.RemoveCounter(counter_handle)
						counter_handle = None
					if hq != None:
						win32pdh.CloseQuery(hq)
						hq = None
				except:
					pass
				
			# SHouldn't get here...we hope!
			return None
	
		def OnTestFinished(self):
			if not self.StartOnCall or not self._IsDebuggerAlive():
				return
			
			self._StopDebugger()
		
		def GetMonitorData(self):
			'''
			Get any monitored data.
			'''
			
			fd = open(self.tempfile, "rb+")
			self.crashInfo = pickle.loads(fd.read())
			fd.close()
			
			try:
				os.unlink(self.tempfile)
			except:
				pass
			
			if self.crashInfo != None:
				ret = self.crashInfo
				self.crashInfo = None
				return ret
			
			return None
		
		def DetectedFault(self):
			'''
			Check if a fault was detected.
			'''
			
			if self.thread and self.thread.is_alive():
				time.sleep(0.15)

			if not self.handlingFault.is_set():
				return False
			
			self.handledFault.wait()
			
			return True
		
		def OnFault(self):
			'''
			Called when a fault was detected.
			'''
			self._StopDebugger()
		
		def OnShutdown(self):
			'''
			Called when Agent is shutting down.
			'''
			self._StopDebugger()

except:
	# Only complain on Windows platforms.
	if sys.platform == 'win32':
		print "Warning: Windows debugger failed to load: ", sys.exc_info()


def StillCrashing():
	args = { "CommandLine" : cmdLine }
	dbg = WindowsDebugEngine(args)
	dbg._StartDebugger()
	
	for i in range(15):
		if not dbg.DetectedFault():
			time.sleep(1)
	
	dbg._StopDebugger()
	
	return dbg.DetectedFault()

# #################################################################################
# #################################################################################
# #################################################################################
# #################################################################################
# #################################################################################

# Note: this is required for multiprocessing module to work.
if __name__ == '__main__':
	
	import sys,os,time,difflib
	
	print ""
	print "] mincrash v0.1 - Locate minimum crashing change"
	print "] Copyright (c) Michael Eddington\n"
	
	try:
		fuzzedFile = sys.argv[1]
		sampleFile = sys.argv[2]
		testFile = sys.argv[3]
		cmdLine = sys.argv[4]
	except:
		print """Syntax:

  mincrash.py fuzzed.bin origional.bin test.bin "target.exe test.bin"
  
"""
		sys.exit()
	
	fd = open(fuzzedFile, "rb")
	fuzzedData = fd.read()
	fd.close()
	
	fd = open(sampleFile, "rb")
	sampleData = fd.read()
	fd.close()
	
	testData = fuzzedData
	testDataOld = testData
	
	diff = difflib.SequenceMatcher(None, fuzzedData, sampleData)
	opcodesList = diff.get_opcodes()
	opcodesList.reverse()
	for tag, i1, i2, j1, j2 in opcodesList:
		
		if tag == 'equal':
			continue
		
		print ("%7s a[%d:%d] b[%d:%d]" %
			(tag, i1, i2, j1, j2)),
		
		crashingData = testData
		
		if tag == 'replace':
			testData = testData[:i1] + sampleData[j1:j2] + testData[i2:]
		elif tag == 'delete':
			testData = testData[:i1] + testData[i2:]
		elif tag == 'insert':
			testData = testData[:i1] + sampleData[j1:j2] + testData[i2:]
		else:
			continue
	
		fd = open(testFile, "wb+")
		fd.write(testData)
		fd.close()
	
		if StillCrashing():
			print "Accepting (still crashes)"
		
		else:
			print "Rejecting (stopped crashing)"
			testData = crashingData

	#print " * Trying from the front..."
	#
	#while True:
	#	diff = difflib.SequenceMatcher(None, testData, sampleData)
	#	tag, i1, i2, j1, j2 = diff.get_opcodes()[0]
	#		
	#	if tag == 'equal':
	#		tag, i1, i2, j1, j2 = diff.get_opcodes()[1]
	#	
	#	print ("%7s a[%d:%d] b[%d:%d]" %
	#		(tag, i1, i2, j1, j2)),
	#	
	#	crashingData = testData
	#	
	#	if tag == 'replace':
	#		testData = testData[:i1] + sampleData[j1:j2] + testData[i2:]
	#	elif tag == 'delete':
	#		testData = testData[:i1] + testData[i2:]
	#	elif tag == 'insert':
	#		testData = testData[:i1] + sampleData[j1:j2] + testData[i2:]
	#	else:
	#		continue
	#
	#	fd = open(testFile, "wb+")
	#	fd.write(testData)
	#	fd.close()
	#
	#	if StillCrashing():
	#		print "Accepting (still crashes)"
	#	
	#	else:
	#		print "Rejecting (stopped crashing)"
	#		testData = crashingData
	#		break


	print "\n"
	print " * Writing mincrash.bin"
	
	fd = open("mincrash.bin", "wb+")
	fd.write(testData)
	fd.close()
