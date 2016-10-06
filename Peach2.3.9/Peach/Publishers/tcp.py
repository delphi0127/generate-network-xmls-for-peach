
'''
Default included TCP publishers.

@author: Michael Eddington
@version: $Id: tcp.py 2591 2011-11-11 11:27:57Z meddingt $
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

# $Id: tcp.py 2591 2011-11-11 11:27:57Z meddingt $

import socket, time, sys
from Peach.Engine.engine import Engine
from Peach.Engine.common import SoftException, PeachException
from Peach.publisher import Publisher
from Peach.publisher import Timeout
from Peach.publisher import PublisherSoftException
import Peach

def Debug(msg):
	if Peach.Engine.engine.Engine.debug:
		print msg

#class Timeout(SoftException):
#	def __init__(self, msg):
#		self.msg = msg
#	
#	def __str__(self):
#		return self.msg

class Tcp(Publisher):
	'''
	A simple TCP client publisher.
	'''
	
	
	def __init__(self, host, port, timeout = 0.25, throttle = 0):
		'''
		@type	host: string
		@param	host: Remote host
		@type	port: number
		@param	port: Remote port
		@type	timeout: number
		@param	timeout: How long to wait for reponse
		@type	throttle: number
		@param	throttle: How long to wait between connections
		'''
		Publisher.__init__(self)
		self._host = host
		
		try:
			self._port = int(port)
		except:
			raise PeachException("The Tcp publisher parameter for port was not a valid number.")
		
		try:
			self._timeout = float(timeout)
		except:
			raise PeachException("The Tcp publisher parameter for timeout was not a valid number.")
		
		try:
			self._throttle = float(throttle)
		except:
			raise PeachException("The Tcp publisher parameter for throttle was not a valid number.")
		
		self._socket = None
		
	def start(self):
		pass
	
	def stop(self):
		self.close()
	
	def connect(self):
		'''
		Create connection.
		'''
		self.close()
		
		if self._throttle > 0:
			time.sleep(self._throttle)
		
		# Try connecting many times
		# before we crash.
		for i in range(30):
			try:
				self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				self._socket.connect((self._host,self._port))
				exception = None
				break
			
			except:
				self._socket = None
				exception = sys.exc_info()
			
			# Wait half sec and try again
			time.sleep(1)
		
		if self._socket == None:
			value = ""
			try:
				value = str(exception[1])
			except:
				pass
			
			raise PeachException("TCP onnection attempt failed: %s" % value)
		
		self.buff = ""
		self.pos = 0
	
	def close(self):
		'''
		Close connection if open.
		'''
		try:
			if self._socket != None:
				self._socket.close()
		finally:
			self._socket = None
		
		self.buff = ""
		self.pos = 0
	
	def send(self, data):
		'''
		Send data via sendall.
		
		@type	data: string
		@param	data: Data to send
		'''
		
		if Peach.Engine.engine.Engine.debug:
			print ">>>>>>>>>>>>>>>>"
			print "tcp.Tcp.send():"
			self.hexPrint(data)
			#added by delphi
			hexstr = "\\x".join("{:02x}".format(ord(c)) for c in data)
			print hexstr
			
		
		try:
			self._socket.sendall(data)
		except:
			if Peach.Engine.engine.Engine.debug:
				print "Tcp: Sendall failed: " + str(sys.exc_info()[1])
			raise PublisherSoftException("sendall failed: " + str(sys.exc_info()[1]))
	
	def _receiveBySize(self, size):
		'''
		This is now a buffered receiver.
		
		@rtype: string
		@return: received data.
		'''
		
		# Do we already a have it?
		if size+self.pos < len(self.buff):
			ret = self.buff[self.pos:self.pos+size]
			self.pos += size
			return ret
		
		# Only ask for the diff of what we don't already have
		diffSize = (self.pos+size) - len(self.buff)
		
		try:
			if Peach.Engine.engine.Engine.debug:
				print "Asking for %d, need %d, have %d" % (size, diffSize, len(self.buff)-self.pos)
			
			self._socket.settimeout(self._timeout)
			ret = self._socket.recv(diffSize)
			
			if not ret:
				# Socket was closed
				if Peach.Engine.engine.Engine.debug:
					print "Socket is closed"
				
				raise PublisherSoftException("Socket is closed")
			
			if Peach.Engine.engine.Engine.debug:
				print "<<<<<<<<<<<<<<<<<"
				print "tcp.Tcp.receive():"
				self.hexPrint(ret)
			
			self.buff += ret
			
		except socket.error, e:
			if str(e).find('The socket operation could not complete without blocking') != -1:
				if Peach.Engine.engine.Engine.debug:
					print "timed out waiting for data"
				
				raise Timeout("Timed out waiting for data [%d:%d:%d:%d]" % (len(self.buff), (size+self.pos), size, diffSize))
			
			elif str(e).find('An existing connection was forcibly') != -1:
				if Peach.Engine.engine.Engine.debug:
					print "Socket was closed!"
				
				raise PublisherSoftException("Socket is closed")
			
			else:
				if Peach.Engine.engine.Engine.debug:
					print "recv failed: " + str(sys.exc_info()[1])
				
				raise PublisherSoftException("recv failed: " + str(sys.exc_info()[1]))
		
		finally:
			self._socket.settimeout(None)
		
		ret = self.buff[self.pos:]
		self.pos = len(self.buff)
		return ret
	
	def _receiveByAvailable(self):
		'''
		Receive as much as possible prior to timeout.
		
		@rtype: string
		@return: received data.
		'''
		self._socket.settimeout(self._timeout)
		
		try:
			ret = self._socket.recv(4096)
			
			if not ret:
				raise PublisherSoftException("Socket is closed")
			
			if Peach.Engine.engine.Engine.debug:
				print "<<<<<<<<<<<<<<<<<"
				print "tcp.Tcp.receive():"
				self.hexPrint(ret)
			
			self.buff += ret
			
		except socket.error, e:
			if str(e).find('The socket operation could not complete without blocking') == -1:
				pass
			
			else:
				raise PublisherSoftException("recv failed: " + str(sys.exc_info()[1]))
		
		self._socket.settimeout(None)
		
		ret = self.buff[self.pos:]
		self.pos = len(self.buff)
		return ret
	
	def receive(self, size = None):
		
		if size == None:
			return self._receiveByAvailable()
		else:
			return self._receiveBySize(size)

class TcpListener(Tcp):
	'''
	A TCP Listener publisher.  This publisher
	supports the following state actions:
	
	 * start - Start listening
	 * stop - Stop listeningn nCMuBd7z3
	 * accept - Accept a client connection
	 * close - Close a client connection
	'''
	
	def __init__(self, host, port, timeout = 0.25):
		Tcp.__init__(self, host, port, timeout)
		
		self._listen = None
		self._clientAddr = None
	
	def start(self):
		self.close()
		
		if self._listen == None:
			# Try connection three times befor
			# exiting fuzzer run
			for i in range(3):
				try:
					self._listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					self._listen.bind((self._host,self._port))
					self._listen.listen(1)
					exception = None
					break
				
				except:
					self._listen = None
					exception = sys.exc_info()
				
				time.sleep(0.5)
			
			if self._listen == None:
				value = ""
				try:
					value = str(exception[1])
				except:
					pass
				
				raise PeachException("TCP bind attempt failed: %s" % value)
		
		self.buff = ""
		self.pos = 0
	
	def stop(self):
		try:
			if self._socket != None:
				self._socket.close()
		except:
			pass
		
		finally:
			self._socket = None
		
		# Avoid TIME_WAIT state by not closing our listener
		
		#try:
		#	if self._listen != None:
		#		self._listen.close()
		#except:
		#	pass
		#
		#finally:
		#	self._listen = None
		
	
	def accept(self):
		self.buff = ""
		self.pos = 0
		
		conn, addr = self._listen.accept()
		self._socket = conn
		self._clientAddr = addr
	
	def close(self):
		try:
			if self._socket != None:
				self._socket.close()
		except:
			pass
		finally:
			self._socket = None
	
	def connect(self):
		raise PeachException("Action 'connect' not supported")

try:
	import win32gui, win32con, win32process
	import sys,time, os, signal
	
	class TcpListenerLaunchGui(TcpListener):
		'''
		Does TcpListener goodness and also can laun a program.  After
		some defined amount of time we will try and close the
		GUI application by sending WM_CLOSE than kill it.
		'''
		
		def __init__(self, host, port, windowname, timeout = 0.25):
			TcpListener.__init__(self, host, port, timeout)
			self._windowName = windowname
			
		def stop(self):
			self.closeApp(self._windowName)
			TcpListener.stop(self)
		
		def call(self, method, args):
			'''
			Launch program to consume file
			
			@type	method: string
			@param	method: Command to execute
			@type	args: array of objects
			@param	args: Arguments to pass
			'''
			
			realArgs = [method, "/c", method]
			for a in args:
				realArgs.append(a)
			
			#print "Spawning %s" % method
			os.spawnv(os.P_NOWAIT, os.path.join( os.getenv('SystemRoot'), 'system32','cmd.exe'), realArgs)
			
	
		def enumCallback(hwnd, windowName):
			'''
			Will get called by win32gui.EnumWindows, once for each
			top level application window.
			'''
			
			try:
			
				# Get window title
				title = win32gui.GetWindowText(hwnd)
				
				# Is this our guy?
				if title.find(windowName) == -1:
					return
				
				(threadId, processId) = win32process.GetWindowThreadProcessId(hwnd)
				
				# Send WM_CLOSE message
				try:
					win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
					win32gui.PostQuitMessage(hwnd)
				except:
						pass
				
				# Give it upto 5 sec
				for i in range(100):
					if win32process.GetExitCodeProcess(processId) != win32con.STILL_ACTIVE:
						# Process exited already
						return
					
					time.sleep(0.25)
				
				try:
					# Kill application
					win32process.TerminateProcess(processId, 0)
				except:
						pass
			except:
				pass
			
		enumCallback = staticmethod(enumCallback)
		
		def closeApp(self, title):
			'''
			Close Application by window title
			'''
			#print "CloseApp: %s" % title
			win32gui.EnumWindows(TcpListenerLaunchGui.enumCallback, title)
		
except:
	pass

# end

