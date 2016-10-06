
'''
Some GUI related monitors.

@author: Michael Eddington
@version: $Id$
'''

#
# Copyright (c) 2008 Michael Eddington
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

# $Id$

try:
	
	import win32gui, win32con
	import sys,time, os, signal
	from threading import *
	from Peach.agent import *
	
	class _WindowWatcher(Thread):
		'''
		Look one child deep on each top level window to try
		and locate dialog boxen.
		'''
		
		def __init__(self):
			Thread.__init__(self)
		
			self.CloseWindows = False
			self.FoundWindowEvent = None # Will be Event()
			self.WindowNames = None # Will be []
			self.StopEvent = None # Will be Event()
		
		def enumCallback(hwnd, self):
			title = win32gui.GetWindowText(hwnd)
			
			for name in self.WindowNames:
				if title.find(name) > -1:
					try:
						self.FoundWindowEvent.set()
						
						if self.CloseWindows:
							win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
					except:
						pass
				else:
					try:
						win32gui.EnumChildWindows(hwnd, _WindowWatcher.enumChildCallback, self)
					except:
						pass
					
			return True
		enumCallback = staticmethod(enumCallback)
		
		def enumChildCallback(hwnd, self):
			title = win32gui.GetWindowText(hwnd)
			
			for name in self.WindowNames:
				if title.find(name) > -1:
					try:
						self.FoundWindowEvent.set()
						
						if self.CloseWindows:
							win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
					except:
						pass
					
			return True
		enumChildCallback = staticmethod(enumChildCallback)
		
		def run(self):
			while not self.StopEvent.isSet():
				win32gui.EnumWindows(_WindowWatcher.enumCallback, self)
				time.sleep(.2)
	
	
	class PopupWatcher(Monitor):
		'''
		Will watch for specific dialogs and optionally kill
		or log a fault when detected.
		'''
		
		def __init__(self, args):
			'''
			Constructor.  Arguments are supplied via the Peach XML
			file.
			
			@type	args: Dictionary
			@param	args: Dictionary of parameters
			'''
			
			# Our name for this monitor
			self._name = "PopupWatcher"
			self._closeWindows = False
			self._triggerFaults = False
			
			if args.has_key("CloseWindows"):
				if args["CloseWindows"].replace("'''", "").lower() in ["yes", "true", "1"]:
					self._closeWindows = True
			
			if args.has_key("TriggerFaults"):
				if args["TriggerFaults"].replace("'''", "").lower() in ["yes", "true", "1"]:
					self._triggerFaults = True
			
			if not args.has_key("WindowNames"):
				raise Exception("PopupWatcher requires a parameter named WindowNames.")
			
			self._names = args["WindowNames"].replace("'''", "").split(',')
		
		def OnTestStarting(self):
			'''
			Called right before start of test case or variation
			'''
			
			self._thread = _WindowWatcher()
			
			self._thread.CloseWindows = self._closeWindows
			self._thread.FoundWindowEvent = Event()
			self._thread.WindowNames = self._names
			self._thread.StopEvent = Event()
			
			self._thread.start()
		
		def OnTestFinished(self):
			'''
			Called right after a test case or varation
			'''
			self._thread.StopEvent.set()
			time.sleep(.6)
		
		def DetectedFault(self):
			'''
			Check if a fault was detected.
			'''
			if self._triggerFaults:
				return self._thread.FoundWindowEvent.isSet()
			
			return False
		
		def OnShutdown(self):
			'''
			Called when Agent is shutting down, typically at end
			of a test run or when a Stop-Run occurs
			'''
			try:
				self._thread.StopEvent.set()
				time.sleep(.6)
			except:
				pass

except:
	pass

# end
