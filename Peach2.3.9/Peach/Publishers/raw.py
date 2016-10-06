
'''
Default included Raw publishers.

@author: Adam Cecchetti
@version: $Id: raw.py 2598 2011-11-15 00:00:43Z egriko $
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
#   Adam Cecchetti (adam@cecchetti.com)
#   Michael Eddington (mike@phed.org)

# $Id: raw.py 2598 2011-11-15 00:00:43Z egriko $


import socket, time, sys
from Peach.publisher import Publisher

class RawEther(Publisher):
	'''
	A simple Raw publisher.
	'''
	
	
	def __init__(self, interface, timeout = 0.1):
		'''
		@type	host: string
		@param	host: Remote host
		@type	timeout: number
		@param	timeout: How long to wait for reponse
		'''
		Publisher.__init__(self)
		self._host = None
		self._socket = None
		self._interface = interface
		self._timeout = float(timeout)
	
	def start(self):
		'''
		Create connection.
		'''
		pass
	
	def stop(self):
		'''
		Close connection if open.
		'''
		self.close()
	
	def connect(self):
		if self._socket != None:
			# Close out old socket first
			self._socket.close()
		self._socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
		self._socket.bind((self._interface,0))
	
	def close(self):
		if self._socket != None:
			self._socket.close()
			self._socket = None
	
	def send(self, data):
		'''
		Send data via sendall.
		
		@type	data: string
		@param	data: Data to send
		'''
		self._socket.sendall(data)
	
	def receive(self, size = None):
		'''
		Receive upto 10000 bytes of data.
		
		@rtype: string
		@return: received data.
		'''
		
		if size != None:
			return self._socket.recv(size)
		
		else:
			self._socket.setblocking(0)
			
			timeout = self._timeout
			beginTime = time.time()
			ret = ''
			
			try:
				while True:
					if len(ret) > 0 or time.time() - beginTime > timeout:
						break
					
					try:
						ret += self._socket.recv(10000)
					except socket.error, e:
						if str(e).find('The socket operation could not complete without blocking') == -1:
							raise
				
			except socket.error, e:
				print "Socket:Receive():  Caught socket.error [%s]" % e
			
			self._socket.setblocking(1)
			return ret


class Raw(Publisher):
	'''
	A simple Raw publisher.
	'''
	
	
	def __init__(self, interface, timeout = 0.1):
		'''
		@type	host: string
		@param	host: Remote host
		@type	timeout: number
		@param	timeout: How long to wait for reponse
		'''
		Publisher.__init__(self)
		self._host = None
		self._socket = None
		self._interface = interface
		self._timeout = float(timeout)
	
	def start(self):
		'''
		Create connection.
		'''
		pass
	
	def stop(self):
		'''
		Close connection if open.
		'''
		self.close()
	
	def connect(self):
		if self._socket != None:
			# Close out old socket first
			self._socket.close()
		self._socket = socket.socket(socket.AF_INET, socket.SOCK_RAW)
		self._socket.bind((self._interface,0))
	
	def close(self):
		if self._socket != None:
			self._socket.close()
			self._socket = None
	
	def send(self, data):
		'''
		Send data via sendall.
		
		@type	data: string
		@param	data: Data to send
		'''
		self._socket.sendall(data)
	
	def receive(self, size = None):
		'''
		Receive upto 10000 bytes of data.
		
		@rtype: string
		@return: received data.
		'''
		
		if size != None:
			return self._socket.recv(size)
		
		else:
			self._socket.setblocking(0)
			
			timeout = self._timeout
			beginTime = time.time()
			ret = ''
			
			try:
				while True:
					if len(ret) > 0 or time.time() - beginTime > timeout:
						break
					
					try:
						ret += self._socket.recv(10000)
					except socket.error, e:
						if str(e).find('The socket operation could not complete without blocking') == -1:
							raise
				
			except socket.error, e:
				print "Socket:Receive():  Caught socket.error [%s]" % e
			
			self._socket.setblocking(1)
			return ret

class RawIp(Publisher):
	'''
	A simple Raw publisher.
	'''
	
	
	def __init__(self, interface, timeout = 0.1):
		'''
		@type	host: string
		@param	host: Remote host
		@type	timeout: number
		@param	timeout: How long to wait for reponse
		'''
		Publisher.__init__(self)
		self._host = None
		self._socket = None
		self._interface = interface
		self._timeout = float(timeout)
	
	def start(self):
		'''
		Create connection.
		'''
		pass
	
	def stop(self):
		'''
		Close connection if open.
		'''
		self.close()
	
	def connect(self):
		if self._socket != None:
			# Close out old socket first
			self._socket.close()

		# Include IP headers
		self._socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
		self._socket.bind((self._interface,0))
		self._socket.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
	
	def close(self):
		if self._socket != None:
			self._socket.close()
			self._socket = None
	
	def send(self, data):
		'''
		Send data via sendall.
		
		@type	data: string
		@param	data: Data to send
		'''
		self._socket.sendall(data)
	
	def receive(self, size = None):
		'''
		Receive upto 10000 bytes of data.
		
		@rtype: string
		@return: received data.
		'''
		
		if size != None:
			return self._socket.recv(size)
		
		else:
			self._socket.setblocking(0)
			
			timeout = self._timeout
			beginTime = time.time()
			ret = ''
			
			try:
				while True:
					if len(ret) > 0 or time.time() - beginTime > timeout:
						break
					
					try:
						ret += self._socket.recv(10000)
					except socket.error, e:
						if str(e).find('The socket operation could not complete without blocking') == -1:
							raise
				
			except socket.error, e:
				print "Socket:Receive():  Caught socket.error [%s]" % e
			
			self._socket.setblocking(1)
			return ret

class Raw6(Publisher):
	'''
	A simple Raw publisher.
	'''
	
	
	def __init__(self, dest_addr, timeout = 0.1):
		'''
		@type	host: string
		@param	host: Remote host
		@type	timeout: number
		@param	timeout: How long to wait for reponse
		'''
		Publisher.__init__(self)
		self._host = None
		self._socket = None
		self._dest_addr  = dest_addr
		self._timeout = float(timeout)
	
	def start(self):
		'''
		Create connection.
		'''
		pass
	
	def stop(self):
		'''
		Close connection if open.
		'''
		self.close()
	
	def connect(self):
		if self._socket != None:
			# Close out old socket first
			self._socket.close()
		
		try:
			self._socket = socket.socket(23, socket.SOCK_RAW, socket.IPPROTO_IPV6)
		except:
			self._socket = socket.socket(socket.AF_INET6, socket.SOCK_RAW, socket.IPPROTO_IPV6)
	
	def close(self):
		if self._socket != None:
			self._socket.close()
			self._socket = None
	
	def send(self, data):
		'''
		Send data via sendall.
		
		@type	data: string
		@param	data: Data to send
		'''
		try:
			self._socket.sendto(data, (self._dest_addr, 0, 0, 0))
		except:
			print sys.exc_info()
	
	def receive(self, size = None):
		'''
		Receive upto 10000 bytes of data.
		
		@rtype: string
		@return: received data.
		'''
		
		if size != None:
			return self._socket.recv(size)
		
		else:
			self._socket.setblocking(0)
			
			timeout = self._timeout
			beginTime = time.time()
			ret = ''
			
			try:
				while True:
					if len(ret) > 0 or time.time() - beginTime > timeout:
						break
					
					try:
						ret += self._socket.recv(10000)
					except socket.error, e:
						if str(e).find('The socket operation could not complete without blocking') == -1:
							raise
				
			except socket.error, e:
				print "Socket:Receive():  Caught socket.error [%s]" % e
			
			self._socket.setblocking(1)
			return ret

class RawIp6(Publisher):
	'''
	A simple Raw publisher.
	'''
	
	
	def __init__(self, dest_addr, timeout = 0.1):
		'''
		@type	host: string
		@param	host: Remote host
		@type	timeout: number
		@param	timeout: How long to wait for reponse
		'''
		Publisher.__init__(self)
		self._host = None
		self._socket = None
		self._dest_addr  = dest_addr
		self._timeout = float(timeout)
	
	def start(self):
		'''
		Create connection.
		'''
		pass
	
	def stop(self):
		'''
		Close connection if open.
		'''
		self.close()
	
	def connect(self):
		if self._socket != None:
			# Close out old socket first
			self._socket.close()
		
		try:
			self._socket = socket.socket(23, socket.SOCK_RAW, socket.IPPROTO_RAW)
		except:
			self._socket = socket.socket(socket.AF_INET6, socket.SOCK_RAW, socket.IPPROTO_RAW)
	
	def close(self):
		if self._socket != None:
			self._socket.close()
			self._socket = None
	
	def send(self, data):
		'''
		Send data via sendall.
		
		@type	data: string
		@param	data: Data to send
		'''
		try:
			self._socket.sendto(data, (self._dest_addr, 0, 0, 0))
			#self._socket.sendall(data)
		except:
			print sys.exc_info()
	
	def receive(self, size = None):
		'''
		Receive upto 10000 bytes of data.
		
		@rtype: string
		@return: received data.
		'''
		
		if size != None:
			return self._socket.recv(size)
		
		else:
			self._socket.setblocking(0)
			
			timeout = self._timeout
			beginTime = time.time()
			ret = ''
			
			try:
				while True:
					if len(ret) > 0 or time.time() - beginTime > timeout:
						break
					
					try:
						ret += self._socket.recv(10000)
					except socket.error, e:
						if str(e).find('The socket operation could not complete without blocking') == -1:
							raise
				
			except socket.error, e:
				print "Socket:Receive():  Caught socket.error [%s]" % e
			
			self._socket.setblocking(1)
			return ret

# end

