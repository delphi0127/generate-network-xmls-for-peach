
#
# Copyright (c) 2007 Michael Eddington
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

# $Id: popupkiller.py 2265 2011-01-18 21:53:24Z meddingt $

import win32gui, win32con
import sys,time, os, signal

print "\n] Peach Popup-Killer/Logger v0.2"
print "] Michael Eddington\n"

# Define pops we will kill and/or save.  Format is array of arrays where
# first item in array is partial window title and second
# item is caption of control to click or None to send a 
# WM_CLOSE message

saveFile = 'popupSaves.txt'
popUps = [
#	[ 'Window Title', 						'Text to find',		'Button to click or None for WM_CLOSE', SaveAssert? ],
#	[ 'The page at',						'switch error',		None,					False ],
#	[ 'NSGlue_Assertion',						None,			'&Ignore',				False ],
#	[ 'Opening',							None,			None,					False ],
#	[ 'Microsoft Visual C++ Debug Library',				'isctype.c',		'Ignore',				False ],
#	[ 'Microsoft Visual C++ Debug Library', 			'Run-Time Check',	'Ignore',				True ],
#	[ '[JavaScript Application]',					None,			None,					False ],
	[ 'Visual Studio Just-In-Time',			None,			'No',					False ],
#	[ 'Adobe Reader',	'Adobe Reader could not open',			'OK',					False ],
	]

storedStrings = []

class IgnoreWindow:
	def __init__(self):
		self.closeCppAssert = False
	
	def _savePopup(self, str):
		#if storedStrings.index(str) > -1:
		#	# Already have this one
		#	return
		
		fd = open(saveFile, "a+")
		fd.write("=========================\n")
		fd.write(self.item[0])
		fd.write("\n----\n")
		#fd.write(self.item[1])
		fd.write("\n----\n")
		#fd.write(self.item[2])
		fd.write("\n----\n")
		fd.write(str)
		fd.write("\n=======================\n")
		fd.close()
		
		#storedStrings.append(str)
		
	def enumSubCallback(hwnd, self):
		title = win32gui.GetWindowText(hwnd)
		
		if self.item[1] == None:
			self.foundText = True
		elif title.find(self.item[1]) > -1:
			self.foundText = True
			
			if self.item[3] == True:
				self._savePopup(title)
		
		# If we found the text and already have our hwnd
		if self.foundText == True and self.IgnoreHwnd != None and self.item[2] != None:
			try:
				win32gui.PostMessage(self.IgnoreHwnd, win32con.WM_LBUTTONDOWN, 0, 0)
				win32gui.PostMessage(self.IgnoreHwnd, win32con.WM_LBUTTONUP, 0, 0)
			except:
				pass
		
		# Found the text but need to WM_CLOSE
		elif self.foundText and self.item[2] == None:
			try:
				win32gui.PostMessage(self.IgnoreHwnd, win32con.WM_CLOSE, 0, 0)
				pass
			except:
				pass
		
		# See if we can find the button to click
		elif self.item[2] != None and title.find(self.item[2]) > -1:
			
			# If we found the text all good, close the window.
			if self.foundText == True:
				try:
					win32gui.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, 0, 0)
					win32gui.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, 0)
				except:
					pass
			
			# Otherwise store it for later
			else:
				self.IgnoreHwnd = hwnd
		
		return True
	enumSubCallback = staticmethod(enumSubCallback)
	
	def enumCallback(hwnd, self):
		title = win32gui.GetWindowText(hwnd)
		#print "enumCallback: %s" % title
		
		for item in self.popUps:
			self.item = item
			if title.find(self.item[0]) > -1:
				self._savePopup(title)
				if self.item[1] == None and self.item[2] == None:
					try:
						win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
						pass
					except:
						pass
				
				else:
					try:
						if self.item[2] == None:
							self.IgnoreHwnd = hwnd
						else:
							self.IgnoreHwnd = None
						
						self.foundText = False
						win32gui.EnumChildWindows(hwnd, IgnoreWindow.enumSubCallback, self)
					except:
						pass
		
		return True
	enumCallback = staticmethod(enumCallback)

ignore = IgnoreWindow()
ignore.popUps = popUps

while True:
	time.sleep(.1)
	win32gui.EnumWindows(IgnoreWindow.enumCallback, ignore)

# end
