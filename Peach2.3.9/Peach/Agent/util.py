
'''
General Utility Monitors

@author: Michael Eddington
@version: $Id$
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

# $Id$

import sys, os, shutil
from Peach.agent import Monitor

class CleanupFolder(Monitor):
	'''
	This monitor will remove any files created in a folder during
	a fuzzing iteration.  Greate for removing stale temp files, etc.
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
		self._folder = args['Folder'].replace("'''","")
		self._folderListing = os.listdir(self._folder)
	
	def OnTestStarting(self):
		'''
		Called right after a test case or varation
		'''
		
		listing = os.listdir(self._folder)
		for item in listing:
			if item not in self._folderListing:
				realName = os.path.join(self._folder, item)
				print "CleanupFolder: Removing '%s'" % realName
				
				try:
					os.unlink(realName)
				except:
					pass
				
				try:
					shutil.rmtree(realName)
				except:
					pass

try:
	import win32api, win32con

except:
	pass

class CleanupRegistry(Monitor):
	'''
	This monitor will remove any sub-keys for a specified registry key
	before each run.  This is usefull for removing document recovery keys
	for fuzzing Office.
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
		self._key = args['Key'].replace("'''","")
		
		if self._key.startswith("HKCU\\"):
			self._root = win32con.HKEY_CURRENT_USER
		elif self._key.startswith("HKCC\\"):
			self._root = win32con.HKEY_CURRENT_CONFIG
		elif self._key.startswith("HKLM\\"):
			self._root = win32con.HKEY_LOCAL_MACHINE
		elif self._key.startswith("HKPD\\"):
			self._root = win32con.HKEY_PERFORMANCE_DATA
		elif self._key.startswith("HKU\\"):
			self._root = win32con.HKEY_USERS
		else:
			print "CleanupRegistry: Error, key must be prefixed with: HKCU, HKCC, HKLM, HKPD, or HKU."
			raise Exception("CleanupRegistry: Error, key must be prefixed with: HKCU, HKCC, HKLM, HKPD, or HKU.")
		
		self._key = self._key[self._key.find("\\")+1:]
	
	def OnTestStarting(self):
		self.deleteKey(self._root, self._key)
	
	def deleteKey(self, hKey, subKey):
		'''
		Recursively remove registry keys
		'''
		
		try:
			hKey = win32api.RegOpenKeyEx(hKey, subKey, 0, win32con.KEY_ALL_ACCESS)
			
			try:
				i = 0
				while True:
					s = win32api.RegEnumKey(hKey, 0)
					self.deleteKey(hKey, s)
					
					print "CleanupRegistry: Removing sub-key '%s'" % s
					win32api.RegDeleteKey(hKey, s)
			
			except win32api.error:
				pass
			finally:
				win32api.RegCloseKey(hKey)
		except:
			print "Warning: Unable to open registry key!"
			pass

	

# end
