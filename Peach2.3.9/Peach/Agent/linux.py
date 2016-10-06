
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

# $Id: peach.py 1986 2010-03-05 07:19:57Z meddingt $

import struct, sys, time
from Peach.agent import Monitor
import os, re, pickle


class LinuxApport(Monitor):
	'''
	Monitor crash reporter for log files.
	
	TODO - Monitor syslog for crash event, then wait for report
	'''
	def __init__(self, args):
		'''
		Constructor.  Arguments are supplied via the Peach XML
		file.
		
		@type	args: Dictionary
		@param	args: Dictionary of parameters
		'''
		
		if args.has_key('Executable'):
			self.Executable = str(args['Executable']).replace("'''", "")
		else:
			self.Executable = None
		
		if args.has_key('LogFolder'):
			self.logFolder = str(args['LogFolder']).replace("'''", "")
		else:
			self.logFolder = "/var/crash/"
		
		if not args.has_key('PeachApport'):
			raise PeachException("Error, LinuxApport monitor requires the PeachApport parameter providing full path to \"peach-apport\" program.")
		
		self.PeachApport = str(args['PeachApport']).replace("'''", "")
		
		# Our name for this monitor
		self._name = "LinuxApport"
		
		self.data = None
		self.startingFiles = None
		
		os.system('echo "|' + self.PeachApport +' %p %s %c" > /proc/sys/kernel/core_pattern')
		os.system('rm -rf ' + self.logFolder + '/*')
	
	
	def OnTestStarting(self):
		'''
		Called right before start of test case or variation
		'''
		
		# Monitor folder
		self.startingFiles = os.listdir(self.logFolder)
	
	def OnTestFinished(self):
		'''
		Called right after a test case or varation
		'''
		pass
	
	def GetMonitorData(self):
		'''
		Get any monitored data from a test case.
		'''
		
		if self.data == None:
			return None
		
		return {"LinuxApport-Crash.txt":self.data}
	
	def DetectedFault(self):
		'''
		Check if a fault was detected.
		'''
		
		try:
			# Give crash reporter time to find the crash
			time.sleep(0.25)
			time.sleep(0.25)
			
			self.data = None
			for f in os.listdir(self.logFolder):
				if not f in self.startingFiles and (self.Executable == None or f.find(self.Executable) > -1):
					fd = open(os.path.join(self.logFolder, f), "rb")
					self.data = fd.read()
					fd.close()
					
					os.unlink(os.path.join(self.logFolder, f))
					
					return True
				
			
			return False
		
		except:
			print sys.exc_info()
		
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
		
		# Stop calling our script
		os.system('echo "" > /proc/sys/kernel/core_pattern')
	
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


# end
