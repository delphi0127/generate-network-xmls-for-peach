
'''
Publish to Peach kernel driver

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

import win32api, win32file
import time, sys, os, ctypes
from Peach.publisher import Publisher

class WindowsKernel(Publisher):

	IOCTL_PEACH_METHOD_START = 2621449216
	IOCTL_PEACH_METHOD_STOP = 2621449220
	IOCTL_PEACH_METHOD_DATA = 2621449224
	IOCTL_PEACH_METHOD_CALL = 2621449228
	IOCTL_PEACH_METHOD_PROPERTY = 2621449232
	IOCTL_PEACH_METHOD_NEXT = 2621449236

	def __init__(self):
		#: Indicates which method should be called.
		self.withNode = False
		self.hDevice = None

	def start(self):
		'''
		Change state such that send/receave will work.  For Tcp this
		could be connecting to a remote host
		'''
		
		if self.hDevice == None:
			self.hDevice = win32file.CreateFile(
				"\\\\.\\Peach",
				win32file.GENERIC_READ|win32file.GENERIC_WRITE,
				0,
				None,
				win32file.CREATE_ALWAYS,
				win32file.FILE_ATTRIBUTE_NORMAL,
				None)
		
		buff = "START!"
		bytesReturned = 0
		
		win32file.DeviceIoControl ( self.hDevice,
			self.IOCTL_PEACH_METHOD_START,
			buff,
			1)
	
	def stop(self):
		'''
		Change state such that send/receave will not work.  For Tcp this
		could be closing a connection, for a file it might be closing the
		file handle.
		'''
		
		if self.hDevice == None:
			return
		
		buff = "STOP!"
		bytesReturned = 0
		
		win32file.DeviceIoControl(self.hDevice,
			self.IOCTL_PEACH_METHOD_STOP,
			buff,
			1)
		
		win32api.CloseHandle(self.hDevice)
		self.hDevice = None
	
	def send(self, data):
		'''
		Publish some data
		
		@type	data: string
		@param	data: Data to publish
		'''
		
		if len(data) == 0:
			print "WindowsKernelDriver: Skipping send with zero bytes."
			return
		
		win32file.DeviceIoControl(self.hDevice,
			self.IOCTL_PEACH_METHOD_DATA,
			data, 1)
	
	def receive(self, size = None):
		'''
		Receive some data.
		
		@type	size: integer
		@param	size: Number of bytes to return
		@rtype: string
		@return: data received
		'''
		raise PeachException("Action 'receive' not supported by publisher")
	
	def call(self, method, args):
		'''
		Call a method using arguments.
		
		@type	method: string
		@param	method: Method to call
		@type	args: Array
		@param	args: Array of strings as arguments
		@rtype: string
		@return: data returned (if any)
		'''
		
		win32file.DeviceIoControl(self.hDevice,
			self.IOCTL_PEACH_METHOD_CALL,
			method,
			1)
		
		for data in args:
			win32file.DeviceIoControl(self.hDevice,
				self.IOCTL_PEACH_METHOD_DATA,
				data,
				1)
	
	def property(self, property, value = None):
		'''
		Get or set property
		
		@type	property: string
		@param	property: Name of method to invoke
		@type	value: object
		@param	value: Value to set.  If None, return property instead
		'''
		
		win32file.DeviceIoControl(self.hDevice,
			self.IOCTL_PEACH_METHOD_PROPERTY,
			property,
			1)
		
		win32file.DeviceIoControl(self.hDevice,
			self.IOCTL_PEACH_METHOD_DATA,
			value,
			1)
	
	def connect(self):
		'''
		Called to connect or open a connection/file.
		'''
		
		pass
		
	def close(self):
		'''
		Close current stream/connection.
		'''
		pass


# end
