
'''
Use the Agent system to have remote Publishers

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

from Peach.Engine.engine import Engine
from Peach.publisher import *

class RemotePublisher(Publisher):
	'''
	Load a publisher on a remote Agent
	'''
	
	def __init__(self, agentName, name, cls, *args):
		Publisher.__init__(self)
		self._agentName = agentName
		self._name = name
		self._cls = cls
		self._args = args
		self._initialized = False
		
	def start(self):
		if self._initialized == False:
			self._agent = Engine.context.agent[self._agentName]
			self._agent.PublisherInitialize(self._name, self._cls, self._args)
			self._initialized = True

		self._agent.PublisherStart(self._name)
	
	def stop(self):
		self._agent.PublisherStop(self._name)
	
	def send(self, data):
		self._agent.PublisherSend(self._name, data)
	
	def receive(self, size = None):
		self._agent.PublisherReceive(self._name, size)
	
	def call(self, method, args):
		self._agent.PublisherCall(self._name, method, args)

	def property(self, property, value = None):
		self._agent.PublisherProperty(self._name, value)
	
	def connect(self):
		self._agent.PublisherConnect(self._name)

	def accept(self):
		self._agent.PublisherAccept(self._name)

	def close(self):
		self._agent.PublisherClose(self._name)



# end
