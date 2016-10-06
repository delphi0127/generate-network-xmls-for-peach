'''
Some helper classes used from Peach
'''

import os, sys
sys.path.append("..")

from Peach.publisher import *
import Peach

class UnittestPublisher(Publisher):
	'''
	Instead of outputting data we call some callback methods.
	'''
	
	callback = None
	
	def accept(self):
		pass
	
	def connect(self):
		pass
	
	def close(self):
		pass
	
	def send(self, data):
		if UnittestPublisher.callback != None:
			callback.PublisherSend(data)
	
	def receive(self):
		return ''
	
	def call(self, method, args):
		if UnittestPublisher.callback != None:
			callback.PublisherCall(method, args)
		
		return ''

class UnittestEngineWatcher(Peach.Engine.engine.EngineWatcher):
	'''
	Perform things needed for unittests.  Also display less verbose output.
	'''
	
	def setTotalVariations(self, totalVariations):
		self.totalVariations = totalVariations
		
	def OnRunStarting(self, run):
		print '[*] Starting run "%s"' % run.name
	
	def OnRunFinished(self, run):
		print '[*] Run "%s" completed' % run.name
	
	def OnTestStarting(self, run, test, totalVariations):
		print '[-] Test: "%s" (%s)' % (test.name, test.description)
		self.totalVariations = '?'
	
	def OnTestFinished(self, run, test):
		print '[-] Test "%s" completed' % (test.name)
	
	def OnTestCaseStarting(self, run, test, variationCount):
		'''
		Called on start of a test case.
		'''
		self.variationCount = variationCount
		
		if variationCount % 500 == 0:
			print "[%d:%s]" % (variationCount, str(self.totalVariations))
	
	def OnTestCaseReceived(self, run, test, variationCount, value):
		'''
		Called when data is received from test case.
		'''
		pass
	
	def OnTestCaseException(self, run, test, variationCount, exception):
		'''
		Called when an exception occurs during a test case.
		'''
		pass
	
	def OnTestCaseFinished(self, run, test, variationCount, actionValues):
		'''
		Called when a test case has completed.
		'''
		pass
	
	def OnFault(self, run, test, variationCount, monitorData, value):
		pass
	
	def OnStopRun(self, run, test, variationCount, monitorData, value):
		pass

# end
