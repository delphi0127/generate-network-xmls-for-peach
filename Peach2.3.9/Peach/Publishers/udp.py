
'''
Default UDP publishers.

@author: Michael Eddington
@version: $Id: udp.py 2240 2010-12-09 02:01:37Z meddingt $
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

# $Id: udp.py 2240 2010-12-09 02:01:37Z meddingt $

import socket, time,sys
from Peach.publisher import *
import Peach

def Debug(msg):
	if Peach.Engine.engine.Engine.debug:
		print msg

class Udp(Publisher):
	'''
	A simple UDP publisher.
	'''
	
	def __init__(self, host, port, timeout = 2):
		'''
		@type	host: string
		@param	host: Remote hostname
		@type	port: number
		@param	port: Remote port
		'''
		Publisher.__init__(self)
		self._host = host
		self._port = port
		self._timeout = float(timeout)
		
		if self._timeout == None:
			self._timeout = 2
		
		self._socket = None
		self.buff = ""
		self.pos = 0
	
	def stop(self):
		'''Close connection if open'''
		self.close()
	
	def close(self):
		if self._socket != None:
			self._socket.close()
			self._socket = None
		self.buff = ""
		self.pos = 0
	
	def connect(self):
		if self._socket != None:
			# Close out old socket first
			self._socket.close()
		self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self._socket.connect((self._host,int(self._port)))
		self.buff = ""
		self.pos = 0
	
	def send(self, data):
		'''
		Send data via sendall.
		
		@type	data: string
		@param	data: Data to send
		'''
		try:
			self._socket.sendall(data)
		except socket.error:
			pass
	
	def receive(self, size = None):
		try:
			self._socket.settimeout(self._timeout)
			data,addr = self._socket.recvfrom(65565)
			
			if hasattr(self, "publisherBuffer"):
				self.publisherBuffer.haveAllData = True
			
			return data
		
		except:
			raise Timeout("")
		
class Udp6(Publisher):
	'''
	A simple UDP publisher.
	'''
	
	def __init__(self, host, port, timeout = 2):
		'''
		@type	host: string
		@param	host: Remote hostname
		@type	port: number
		@param	port: Remote port
		'''
		Publisher.__init__(self)
		self._host = host
		self._port = port
		self._timeout = float(timeout)
		
		if self._timeout == None:
			self._timeout = 2
		
		self._socket = None
		self.buff = ""
		self.pos = 0
	
	def stop(self):
		'''Close connection if open'''
		self.close()
	
	def close(self):
		if self._socket != None:
			self._socket.close()
			self._socket = None
		self.buff = ""
		self.pos = 0
	
	def connect(self):
		if self._socket != None:
			# Close out old socket first
			self._socket.close()
		
		self._socket = socket.socket(23, socket.SOCK_DGRAM)
		self._socket.connect((self._host,int(self._port)))
		self.buff = ""
		self.pos = 0
	
	def send(self, data):
		'''
		Send data via sendall.
		
		@type	data: string
		@param	data: Data to send
		'''
		try:
			self._socket.sendall(data)
		except socket.error:
			pass
	
	def receive(self, size = None):
		data = None
		try:
			self._socket.settimeout(self._timeout)
			data,addr = self._socket.recvfrom(65565)
			
			if hasattr(self, "publisherBuffer"):
				self.publisherBuffer.haveAllData = True
			
			return data
		except:
			if data == None or len(data) < size:
				raise Timeout("")
			
			return data
		
class UdpListener(Publisher):
	'''
	A simple UDP publisher.
	'''
	
	def __init__(self, host, port, timeout = 2):
		'''
		@type	host: string
		@param	host: Remote hostname
		@type	port: number
		@param	port: Remote port
		'''
		Publisher.__init__(self)
		self._host = host
		self._port = port
		self._timeout = float(timeout)
		
		if self._timeout == None:
			self._timeout = 2
			
		self._socket = None
			
	def stop(self):
		'''Close connection if open'''
		self.close()
			
	def close(self):
		if self._socket != None:
			self._socket.close()
			self._socket = None
			
	def connect(self):
		if self._socket != None:
			# Close out old socket first
			self._socket.close()
		self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self._socket.bind((self._host,int(self._port)))
		
	def send(self, data):
		'''
		Send data via sendall.
		
		@type	data: string
		@param	data: Data to send
		'''
		try:
			self._socket.sendto(data, self.addr)
		
		except socket.error:
			pass
	
	def receive(self, size = None):
		data,self.addr = self._socket.recvfrom(65565)
		
		if hasattr(self, "publisherBuffer"):
			self.publisherBuffer.haveAllData = True
			
		return data

class Udp6Listener(Publisher):
	'''
	A simple UDP publisher.
	'''
	
	def __init__(self, host, port, timeout = 2):
		'''
		@type	host: string
		@param	host: Remote hostname
		@type	port: number
		@param	port: Remote port
		'''
		Publisher.__init__(self)
		self._host = host.lower()
		self._port = port
		self._timeout = float(timeout)
		
		if self._timeout == None:
			self._timeout = 2
			
		self._socket = None
			
	def stop(self):
		'''Close connection if open'''
		self.close()
			
	def close(self):
		if self._socket != None:
			self._socket.close()
			self._socket = None
			
	def connect(self):
		if self._socket != None:
			# Close out old socket first
			self._socket.close()
		self._socket = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
		self._socket.bind(("",int(self._port)))
		
	def send(self, data):
		'''
		Send data via sendall.
		
		@type	data: string
		@param	data: Data to send
		'''
		try:
			self._socket.sendto(data, self.addr)
		
		except socket.error:
			pass
	
	def receive(self, size = None):
		while True:
			data,self.addr = self._socket.recvfrom(65565)
			if self.addr[0].lower().find(self._host) != -1:
				break
		
		if hasattr(self, "publisherBuffer"):
			self.publisherBuffer.haveAllData = True
		
		return data

# end
