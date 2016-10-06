'''
Peach Logging System

This is the Peach logging sub-system.  To implement a new logging method
extend from Logger.

@author: Michael Eddington
@version: $Id: logger.py 2979 2012-08-28 20:32:13Z meddingt $
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

# $Id: logger.py 2979 2012-08-28 20:32:13Z meddingt $

import sys, os
from Engine.engine import EngineWatcher
from Engine.engine import Engine

class Logger(EngineWatcher):
	'''
	Parent class for all logger implementations.
	'''
	
	def OnCrashOrBreak(self):
		'''
		Called when we are exiting due to crash or Ctrl+BREAK/Ctrl+C.
		'''
		pass
	
	def OnRunStarting(self, run):
		'''
		Called when a run is starting.
		'''
		pass
	
	def OnRunFinished(self, run):
		'''
		Called when a run is finished.
		'''
		pass
	
	def OnTestStarting(self, run, test, totalVariations):
		'''
		Called on start of a test.  Each test has multiple variations.
		'''
		pass
	
	def OnTestFinished(self, run, test):
		'''
		Called on completion of a test.
		'''
		pass

	def OnTestCaseStarting(self, run, test, variationCount):
		'''
		Called on start of a test case.
		'''
		pass
	
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

import os,uuid
from time import *

class Filesystem(Logger):
	'''
	A file system logger.
	'''
	
	def __init__(self, params):
		self.name = str(uuid.uuid1())
		self.elementType = 'logger'
		self.params = params
		self.heartBeat = 512
		self.file = None
		self.lastTestCount = 0
		self.firstIter = True
	
	def _writeMsg(self, line):
		self.file.write(asctime() + ": " + line + "\n")
		self.file.flush()
		
	def OnCrashOrBreak(self):
		'''
		Called when we are exiting due to crash or Ctrl+BREAK/Ctrl+C.
		'''
		if self.file != None:
			self._writeMsg("FORCED EXIT OR CRASH!")
			self._writeMsg("Last test #: %d" % self.lastTestCount)
	
	def OnRunStarting(self, run):
		suppliedPath = str(self.params['path']).replace("'''", "")
		pitFile = os.path.basename(Engine.context.pitFile)
		
		if run.name == "DefaultRun":
			self.path = os.path.join(suppliedPath, pitFile + "_" + strftime("%Y%b%d%H%M%S", gmtime()))
		else:
			self.path = os.path.join(suppliedPath, pitFile + "_" + run.name + "_" + strftime("%Y%b%d%H%M%S", gmtime()))
		
		self.faultPath = os.path.join(self.path, "Faults")
		try:
			os.mkdir(suppliedPath)
		except:
			pass
		try:
			os.mkdir(self.path)
		except:
			pass
		
		if self.file != None:
			self.file.close()
		
		self.file = open(os.path.join(self.path,"status.txt"), "w")
		
		self.file.write("Peach Fuzzer Run\n")
		self.file.write("=================\n\n")
		self.file.write("Command line: ")
		for arg in sys.argv:
			self.file.write("%s " % arg)
		self.file.write("\n")
		
		self.file.write("Date of run: " + asctime() + "\n")
		
		if Engine.context.SEED != None:
			self.file.write("SEED: %s\n" % Engine.context.SEED)
		
		self.file.write("Pit File: %s\n" % pitFile)
		self.file.write("Run name: " + run.name + "\n\n")
		
		self.lastTestCount = 0
		self.firstIter = True
		
	
	def OnRunFinished(self, run):
		self.file.write("\n\n== Run completed ==\n" + asctime() + "\n")
		self.file.close()
		self.file = None
		self.lastTestCount = 0
	
	def OnTestStarting(self, run, test, totalVariations):
		self._writeMsg("")
		self._writeMsg("Test starting: " + test.name)
		#self._writeMsg("Test has %d variations" % totalVariations)
		self._writeMsg("")
		self.firstIter = True
	
	def OnTestFinished(self, run, test):
		self._writeMsg("")
		self._writeMsg("Test completed: " + test.name)
		self._writeMsg("")
	
	def OnTestCaseException(self, run, test, variationCount, exception):
		pass
	
	def OnFault(self, run, test, variationCount, monitorData, actionValues):
		self._writeMsg("Fault was detected on test %d" % variationCount)
		
		# Look for Bucket information
		bucketInfo = None
		for key in monitorData.keys():
			if key.find("_Bucket") > -1:
				bucketInfo = monitorData[key]
				break
		
		# Build folder structure
		try:
			os.mkdir(self.faultPath)
		except:
			pass
		
		if bucketInfo != None:
			print "BucketInfo:", bucketInfo
			
			bucketInfos = bucketInfo.split(os.path.sep)
			path = self.faultPath
			for p in bucketInfos:
				path = os.path.join(path,p)
				try:
					os.mkdir(path)
				except:
					pass
			
			path = os.path.join(path,str(variationCount))
			try:
				os.mkdir(path)
			except:
				pass
			
		else:
			try:
				path = os.path.join(self.faultPath,"Unknown")
				os.mkdir(path)
			except:
				pass
			
			path = os.path.join(self.faultPath,"Unknown",str(variationCount))
		
		try:
			os.mkdir(path)
		except:
			pass
		
		# Expand actionValues
		
		for i in range(len(actionValues)):
			fileName = os.path.join(path, "data_%d_%s_%s.txt" % (i, actionValues[i][1], actionValues[i][0]))
			
			if len(actionValues[i]) > 2:
				fout = open(fileName, "w+b")
				
				# BUG - reported bug that occationally we crash here.
				try:
					fout.write(actionValues[i][2])
				except:
					print "Error, exception tripped writing out actionValues array.  Ignoring."
					pass
				
				if len(actionValues[i]) > 3 and actionValues[i][1] != 'output':
					fout.write(repr(actionValues[i][3]))
				
				fout.close()
				
				# Output filename from data set if we have it.
				if len(actionValues[i]) > 3 and actionValues[i][1] == 'output':
					self._writeMsg("Origional file name: "+actionValues[i][3])
					
					fileName = os.path.join(path, "data_%d_%s_%s_fileName.txt" % (i, actionValues[i][1], actionValues[i][0]))
					fout = open(fileName, "w+b")
					fout.write(actionValues[i][3])
					fout.close()
		
		for key in monitorData.keys():
			if key.find("_Bucket") == -1:
				fout = open(os.path.join(path,key), "wb")
				fout.write(monitorData[key])
				fout.close()
	
	def OnStopRun(self, run, test, variationCount, monitorData, value):
		self._writeMsg("")
		self._writeMsg("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
		self._writeMsg("!!!! TEST ABORTING AT %d" % variationCount)
		self._writeMsg("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
		self._writeMsg("")
	
	def OnTestCaseStarting(self, run, test, variationCount):
		'''
		Called on start of a test case.
		'''
		if self.firstIter or variationCount > (self.lastTestCount+1) or variationCount % self.heartBeat == 0:
			self._writeMsg("On test variation # %d" % variationCount)
			self.firstIter = False
		self.lastTestCount = variationCount

import xmlrpclib, base64

class KeyValue:
	def __init__(self, key = None, value = None):
		self.key = key
		self.value = value

class PeachManagerLogger(Logger):
	'''
	This logger interacts with the Peach Manager product.
	'''
	
	def __init__(self, params):
		self.name = str(uuid.uuid1())
		self.elementType = 'logger'
		self.params = params
		self.heartBeat = 512
		self._getProxy().Initialized()
		self.totalVariations = 0
		
		self._getProxy().Initialized()
	
	def _getProxy(self):
		return xmlrpclib.ServerProxy("http://127.0.0.1:8081/local.rem")
	
	def OnRunStarting(self, run):
		self._getProxy().RunStarting(run.name)
	
	def OnRunFinished(self, run):
		self._getProxy().RunFinished(run.name)
	
	def OnTestStarting(self, run, test, totalVariations):
		self._getProxy().TestStarting(test.name)
		
		try:
			self.totalVariations = int(totalVariations)
		except:
			self.totalVariations = 0
	
	def OnTestFinished(self, run, test):
		self._getProxy().TestFinished(test.name)
	
	def OnTestCaseException(self, run, test, variationCount, exception):
		self._getProxy().TestCaseException(int(variationCount), str(exception))
	
	def OnFault(self, run, test, variationCount, monitorData, actionValues):
		
		monitorDataKeyValue = []
		actionValuesKeyValue = []
		
		for key in monitorData.keys():
			monitorDataKeyValue.append(KeyValue(key, base64.b64encode(monitorData[key])))
		
		data = ""
		for i in range(len(actionValues)):
			fileName = "data_%d_%s_%s.txt" % (i, actionValues[i][1], actionValues[i][0])
			
			if len(actionValues[i]) > 2:
				data = actionValues[i][2]
				
				if len(actionValues[i]) > 3 and actionValues[i][1] != 'output':
					data = repr(actionValues[i][3])
				
				# Output filename from data set if we have it.
				if len(actionValues[i]) > 3 and actionValues[i][1] == 'output':
					fileName = "data_%d_%s_%s_fileName.txt" % (i, actionValues[i][1], actionValues[i][0])
					data = actionValues[i][3]
			
			actionValuesKeyValue.append(KeyValue(fileName, base64.b64encode(data)))
		
		self._getProxy().Fault(int(variationCount), monitorDataKeyValue, actionValuesKeyValue)
	
	def OnStopRun(self, run, test, variationCount, monitorData, value):
		self._getProxy().StopRun()
		
	def OnTestCaseStarting(self, run, test, variationCount):
		self._getProxy().TestCaseStarting(int(variationCount), int(self.totalVariations))

# end
