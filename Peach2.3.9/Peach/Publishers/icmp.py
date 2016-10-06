
'''
Default included ICMP publishers.

@author: Michael Eddington
@author: Adam Cecchetti
@version: $Id: icmp.py 2020 2010-04-14 23:13:14Z meddingt $
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
#   Adam Cecchetti (adam@cecchetti.com)
#
# $Id: icmp.py 2020 2010-04-14 23:13:14Z meddingt $


import socket, time, sys
from Peach.publisher import Publisher

class Icmp(Publisher):
	'''
	A simple Icmp publisher.
	'''
	
	_host = None
	_socket = None
	
	def __init__(self, host, timeout = 0.1):
		'''
		@type	host: string
		@param	host: Remote host
		@type	timeout: number
		@param	timeout: How long to wait for reponse
		'''
		Publisher.__init__(self)
		self._host = host
		self._timeout = float(timeout)
		
	def stop(self):
		'''
		Close connection if open.
		'''
		self.close()
	
	def connect(self):
		if self._socket != None:
			# Close out old socket first
			self._socket.close()
		self._socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname('icmp'))
		self._socket.connect((self._host,22))
	
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
				print "Tcp::Receive():  Caught socket.error [%s]" % e
			
			self._socket.setblocking(1)
			return ret

# end

