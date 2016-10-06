
'''
vmware controler for Peach Agent.  Allows manipulating the state of a vm
during a fuzzing run.  Common use case here is to revert to a known good
state after a fault or N tests.

@author: Michael Eddington
@version: $Id: vm.py 1665 2009-04-11 21:52:21Z meddingt $
'''

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

# $Id: vm.py 1665 2009-04-11 21:52:21Z meddingt $

import sys
from Peach.agent import Monitor

try:
	from vix import Vix
except:
	pass
	#print "Warning: Module pyvix not found.  VMWare Monitor will not function."

class Vmware(Monitor):
	'''
	Control a vmware server instance to start/revert the
	target vm.
	'''
	
	def __init__(self, args):
		'''
		Start VM
		'''
		
		index = -1
		
		try:
			if args['snapshotindex'] != None:
				index = int(args['snapshotindex'].replace("'''", ""))
		except:
			pass
		
		self.vm = Vix()
		
		try:
			self.vm.Connect(str(args['host']).replace("'''", ""))
		except:
			self.vm.Connect()
		
		print "About to open:", args['vmx']
		self.vm.Open(str(args['vmx']).replace("'''", ""))
		
		if index > -1:
			self.vm.GetRootSnapshot(index)
		else:
			self.vm.GetRootSnapshot()
		
		self.vm.RevertToSnapshot()
	
	def OnFault(self):
		'''
		On a fault, restart VM to save point.
		'''
		self.vm.RevertToSnapshot()
	
	def OnShutdown(self):
		'''
		Shutdown vm
		'''
		self.vm.PowerOff()
		self.vm.Disconnect()

# end
