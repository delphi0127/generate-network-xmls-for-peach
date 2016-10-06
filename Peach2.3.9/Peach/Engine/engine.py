'''
The high level engine that executes a Peach fuzzer run.

The engine component currently does the following:

  1. Accepts a peach XML and parses it
  2. Configures watchers, loggers
  3. Connects to Agents and spinns up Monitors
  4. Runs each defined test
     a. Notified Agents
     b. Calls State Engine


@author: Michael Eddington
@version: $Id: engine.py 2291 2011-03-04 03:41:47Z meddingt $
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

# $Id: engine.py 2291 2011-03-04 03:41:47Z meddingt $

## NOTE: imports are at the bottom.

PROFILE = False

if PROFILE:
	print " --- ENGINE PROFILING ENABLED ---- "
	import profile

class Empty(object):
	pass

class EngineWatcher(object):
	'''
	Base for a class that receives callback when events occur
	in the Peach Engine.
	'''
	
	isElement = False
	isElementWithChildren = False
	isDataElement = False
	
	def setTotalVariations(self, totalVariations):
		self.totalVariations = totalVariations
		
	def OnCrashOrBreak(self):
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
	
	def OnStateEnter(self, state):
		'''
		Called as we enter a state
		'''
		pass
	
	def OnStateExit(self, state):
		'''
		Called as we exit a state
		'''
		pass
	
	def OnActionStart(self, action):
		'''
		Called as we start an action
		'''
		pass
	
	def OnActionComplete(self, action):
		'''
		Called after we completed action
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

class EngineWatchPlexer(EngineWatcher):
	'''
	Allows multiple watchers to be attached and will
	distribute messages out to them.
	'''
	
	def __init__(self):
		self.watchers = []
	
	def setTotalVariations(self, totalVariations):
		for w in self.watchers:
			w.setTotalVariations(totalVariations)
		
	def OnRunStarting(self, run):
		for w in self.watchers:
			w.OnRunStarting(run)
	
	def OnRunFinished(self, run):
		for w in self.watchers:
			w.OnRunFinished(run)
	
	def OnTestStarting(self, run, test, totalVariations):
		for w in self.watchers:
			w.OnTestStarting(run, test, totalVariations)
	
	def OnTestFinished(self, run, test):
		for w in self.watchers:
			w.OnTestFinished(run, test)

	def OnTestCaseStarting(self, run, test, variationCount):
		for w in self.watchers:
			w.OnTestCaseStarting(run, test, variationCount)
	
	def OnTestCaseReceived(self, run, test, variationCount, value):
		for w in self.watchers:
			w.OnTestCaseReceived(run, test, variationCount, value)
	
	def OnTestCaseException(self, run, test, variationCount, exception):
		for w in self.watchers:
			w.OnTestCaseException(run, test, variationCount, exception)
	
	def OnTestCaseFinished(self, run, test, variationCount, actionValues):
		for w in self.watchers:
			w.OnTestCaseFinished(run, test, variationCount, actionValues)
	
	def OnFault(self, run, test, variationCount, monitorData, value):
		for w in self.watchers:
			w.OnFault(run, test, variationCount, monitorData, value)

	def OnStateEnter(self, state):
		for w in self.watchers:
			w.OnStateEnter(state)
	
	def OnStateExit(self, state):
		for w in self.watchers:
			w.OnStateExit(state)
	
	def OnActionStart(self, action):
		for w in self.watchers:
			w.OnActionStart(action)
	
	def OnActionComplete(self, action):
		for w in self.watchers:
			w.OnActionComplete(action)
			
	def OnStopRun(self, run, test, variationCount, monitorData, value):
		for w in self.watchers:
			w.OnStopRun(run, test, variationCount, monitorData, value)


class StdoutWatcher(EngineWatcher):
	'''
	This is the default console interface to Peach
	it prints out information as tests are performed.
	'''
	
	def OnRunStarting(self, run):
		print '[*] Starting run "%s"' % run.name
	
	def OnRunFinished(self, run):
		print '[*] Run "%s" completed' % run.name
	
	def OnTestStarting(self, run, test, totalVariations):
		self.startTime = None
		self.startVariationCount = None
		self.remaingTime = "?"
		self.totalVariations = totalVariations
		
		print '[-] Test: "%s" (%s)' % (test.name, test.description)
	
	def OnTestFinished(self, run, test):
		print '[-] Test "%s" completed' % (test.name)
	
	def OnTestCaseStarting(self, run, test, variationCount):
		
		prefix = "[%d:%s:%s] " % (variationCount,
								 str(self.totalVariations),
								 str(self.remaingTime))
		
		print prefix+"Element: %s" % (test.mutator.currentMutator().changedName)
		
		print (" "*len(prefix)) + "Mutator: %s\n" % (test.mutator.currentMutator().name)
		
		if self.startTime == None and variationCount > 1:
			self.startTime = time.time()
			self.startVariationCount = variationCount
		
		try:
			if variationCount % 20 == 0:
				count = variationCount - (self.startVariationCount - 1)
				elaps = time.time() - self.startTime
				perTest = elaps / count
				remaining = (int(self.totalVariations) - variationCount) * perTest
				self.remaingTime = str(int((remaining / 60) / 60)) + "hrs"
				
				# After a while throw out old stuff
				# and start over.
				if count > 5000:
					self.startTime = time.time()
					self.startVariationCount = variationCount
					
		except:
			pass
	
	def OnTestCaseReceived(self, run, test, variationCount, value):
		
		## TODO: Needs to work with actions...SAD!
		if Engine.verbose:
			print "[%d:%s:%s] Received data: %s" % (variationCount,
												str(self.totalVariations),
												str(self.remaingTime),
												repr(value))
		else:
			print "[%d:%s:%s] Received data" % (variationCount,
												str(self.totalVariations),
												str(self.remaingTime))
	
	def OnTestCaseException(self, run, test, variationCount, exception):
		print "[%d:%s:%s] Caught error on receave, ignoring [%s]" % (variationCount,
											str(self.totalVariations),
											str(self.remaingTime),
											exception)
		
		return True
	
	def OnTestCaseFinished(self, run, test, variationCount, actionValues):
		#print "--------\n"
		pass

class Engine(object):
	"""
	The highlevel Peach engine.  The main entrypoint is "Run(...)" which
	consumes a Peach XML file and performs the fuzzing run.
	"""
	
	#: Toggle display of debug messages.
	debug = False
	#: Use the new matched relation method (faster)
	relationsNew = False
	#: Only do a single iteration
	justOne = False
	#: Use the native cDeepCopy
	nativeDeepCopy = True
	#: Test range
	testRange = None
	#: The Engine instance
	context = None
	
	def __init__(self):
		self.noCount = True
		self.restartFile = None
		self.restartState = None
		self.verbose = False
		Engine.verbose = False
		self.peach = None
		self.agent = None
		self._agents = {}
		self.startNum = None
		Engine.context = self
		
	def Count(self, uri, runName = None):
		"""
		Just count the tests!
		
		@type	uri: String
		@param	uri: URI specifying the filename to use.  Must have protocol prepended (file:, http:, etc)
		@type	runName: String
		@param	runName: Name of run or if None, "DefaultRun" is used.
		"""
		
		print ""
		print "Warning: This will run the fuzzer through several iterations to determine the count."
		print "\n   -- Press Any Key To Continue, or Ctrl+C to Stop -- "
		getch()
		print "\n"
		
		if runName == None:
			runName = "DefaultRun"
		
		self.watcher = EngineWatchPlexer()
		self.peach = Analyzer.DefaultParser().asParser(uri)
		self.agent = AgentPlexer()
		self._agents = {}
		
		if hasattr(self.peach.runs, runName):
			run = getattr(self.peach.runs, runName)
		else:
			raise PeachException("Can't find run %s" % runName)
		
		totalCount = 0
		for test in run.tests:
			testCount = self._countTest(run, test, True)
			totalCount += testCount
			
			print "Test %s has %d test cases" % (test.name, testCount)
		
		print "\nTotal test cases for run %s is %d" % (runName, totalCount)
		return totalCount
	
	def Run(self, uri, runName = None, verbose = False, watcher = None,
			restartFile = None, noCount = False, parallel = None, startNum = None):
		"""
		Run a Peach XML file.
		
		Called by peach.py to perform fuzzing runs.
		
		@type	uri: String
		@param	uri: URI specifying the filename to use.  Must have protocol prepended (file:, http:, etc)
		@type	runName: String
		@param	runName: Name of run or if None, "DefaultRun" is used.
		@type	verbose: Boolean
		@param	verbose: Not used anymore??
		@type	watcher: Instance
		@param	watcher: UI Interface that receaves callbacks from engine
		@type	restartFile: String
		@param	restartFile: File containing state for restarting a fuzzing run
		@type	noCount: Boolean
		@param	noCount: No longer used
		@type	parallel: List
		@param	parallel: First item is total machine count, second is our machine #
		"""
		
		if runName == None:
			runName = "DefaultRun"
		
		self.noCount = noCount
		self.restartFile = restartFile
		self.restartState = None
		self.verbose = verbose
		Engine.verbose = verbose
		
		if uri.find(":") >= 0:
			self.pitFile = uri[uri.find(":")+1:]
		else:
			self.pitFile = uri
		
		if self.pitFile.find("/") >= 0:
			self.pitFile = self.pitFile[uri.rfind("/")+1:]
		
		self.peach = Analyzer.DefaultParser().asParser(uri)
		
		run = None
		self.agent = AgentPlexer()
		self._agents = {}
		self.startNum = startNum
		
		self.watcher = EngineWatchPlexer()
		
		if watcher == None:
			self.watcher.watchers.append(StdoutWatcher())
		else:
			self.watcher.watchers.append(watcher)
		
		if runName != None:
			if hasattr(self.peach.runs, runName):
				run = getattr(self.peach.runs, runName)
			else:
				raise PeachException("Can't find run %s" % runName)
		
		else:
			raise PeachException("Must specify a run name")
			#run = self.peach.runs[0]
		
		logger = run.getLogger()
		if logger != None:
			self.watcher.watchers.append(logger)
		
		try:
			self.watcher.OnRunStarting(run)
		except TypeError, t:
			print t
			print dir(self.watcher)
			print dir(self.watcher.OnRunStarting)
			raise t
		
		skipToTest = False
		if self.restartFile != None:
			
			print ""
			print "-- Restarting based on state file"
			print "-- Loading state file: %s\n" % self.restartFile
			
			fd = open(self.restartFile, "rb+")
			self.restartState = pickle.loads(fd.read())
			fd.close()
			skipToTest = True
			skipToTestName = self.restartState[0]
		
		if parallel == None:
			for test in run.tests:
				self._runPathTest(run, test)
			
			for test in run.tests:
				
				# Skip to specific test if needs be.  Used to
				# restart a test run
				if skipToTest and test.name != skipToTestName:
					continue
				elif skipToTest and test.name == skipToTestName:
					skipToTest = False
				
				self._runTest(run, test, False, self.testRange)
		
		else:
			# Handle parallel fuzzing
			print "-- Parallel fuzzing, configuring test run"
			
			if len(run.tests) > 1:
				raise PeachException("Only a single test per-run is currently supported for parallel fuzzing.")
			
			totalMachines = int(parallel[0])
			thisMachine = int(parallel[1])
			test = run.tests[0]
			
			# 1. Get our total count.  We want to use a copy of everything
			#    so we don't pollute the DOM!
			peach = Analyzer.DefaultParser().asParser(uri)
			
			totalCount = self._countTest(getattr(peach.runs, runName), getattr(peach.runs, runName).tests[0])
			
			# 2. How many tests per machine?
			perCount = int(totalCount / totalMachines)
			leftOver = totalCount - (perCount * totalMachines)
			
			# 3. How many for this machine?
			startCount = thisMachine * perCount
			thisCount = perCount
			if thisMachine == totalMachines-1:
				thisCount += leftOver
			
			print "-- This machine will perform chunk %d through %d out of %d total" % (startCount, startCount+thisCount, totalCount)
			self._runTest(run, test, False, [startCount, startCount+thisCount])
		
		self.watcher.OnRunFinished(run)
	
	def _startAgents(self, run, test):
		'''
		Start up agents listed in test.
		'''
		
		for a in test:
			if a.elementType == 'agent':
				if a.location == 'local':
					server = "."
				else:
					server = a.location
				
				agent = self.agent.AddAgent(a.name, server, a.password, a.getPythonPaths(), a.getImports())
				self._agents[a.name] = agent
				
				# Start monitors for agent
				for m in a:
					if m.elementType == 'monitor':
						agent.StartMonitor(m.name, m.classStr, m.params)
	
	def _stopAgents(self, run, test):
		self.agent.OnShutdown()
		
	def _countTest(self, run, test, verbose = False):
		'''
		Get the total test count of this test
		'''
		
		print "-- Counting total test cases..."
		
		mutator = self._runTest(run, test, True)
		
		if mutator == None:
			cnt = 0
		else:
			cnt = mutator.getCount()
		
		if cnt == None:
			raise PeachException("An error occured counting total tests.")
		
		print "-- Count completed, found %d tests" % cnt
		
		return cnt
	
	def _runTest(self, run, test, countOnly = False, testRange = None):
		'''
		Runs a Test as defined in the Peach XML.
		
		@type	run: Run object
		@param	run: Run that test is part of
		@type	test: Test object
		@param	test: Test to run
		@type	countOnly: bool
		@param	countOnly: Should we just get total mutator count? Defaults to False.
		@type	testRange: list of numbers
		@param	testRange: Iteration # test ranges.  Only used when performing parallel fuzzing.
		
		@rtype: number
		@return: the total number of test iterations or None
		'''
		
		stateMachine = test.stateMachine
		stateEngine = StateEngine(self, stateMachine, test.publishers)
		
		pub = test.publishers
		
		totalTests = "?"
		testCount = 0
		
		# Sping up agents
		self._startAgents(run, test)
		
		if not countOnly:
			self.watcher.OnTestStarting(run, test, totalTests)
		
		# Initialize publishers
		for p in pub:
			p.initialize()
		
		errorCount = 0
		maxErrorCount = 10
		
		# Get all the mutators we will use
		self.mutators = []
		for m in test.getMutators():
			try:
				self.mutators.append(eval(m.name))
			except:
				try:
					self.mutators.append(evalEvent("PeachXml_"+m.name, {}, run))
				except:
					raise PeachException("Unable to load mutator [%s], please verify it was imported correctly." % m.name)
		
		mutator = test.mutator
		value = "StateMachine"
		
		if self.restartState != None:
			print "-- State will load in 1 iteration"
		
		elif testRange != None:
			print "-- Will skip to start of chunk in 1 iteration"
		
		# Needs to be off on its own!
		startCount = None
		endCount = None
		if testRange != None:
			startCount = testRange[0]
			endCount = testRange[1]
		
		if self.startNum != None:
			startCount = self.startNum
		
		redoCount = 0
		saveState = False
		exitImmediate = False
		actionValues = None
		
		try:
			
			while True:
				try:
					testCount += 1
					
					if PROFILE:
						if testCount > 2:
							break
					
					# What if we are just counting?
					if testCount == 2 and countOnly:
						self._stopAgents(run, test)
						return mutator
					
					# Go through one iteration before we load state
					elif testCount == 2 and self.restartState != None:
						print "-- Restoring state"
						testCount = self.restartState[1]
						mutator.setState(self.restartState[2])
					
					elif testCount == 2 and startCount != None and startCount > 2:
						# Skip ahead to start range, but not if we are
						# restoring saved state.
						print "-- Skipping ahead to iteration %d" % startCount
						#testCount -= 1
						for i in range(testCount, startCount):
							mutator.next()
							testCount+=1
					
					# Update total test count
					if testRange == None:
						totalTests = mutator.getCount()
						
					else:
						# if we are parallel use our endCount which will also
						# cause the estimated time left to be correct
						totalTests = endCount+1
					
					if totalTests == -1 or totalTests == None:
						totalTests = "?"
						
					else:
						self.watcher.setTotalVariations(totalTests)
					
					# Fire some events
					self.agent.OnTestStarting()
					
					if not countOnly:
						self.watcher.OnTestCaseStarting(run, test, testCount)
					
					self.testCount = testCount
					mutator.onTestCaseStarting(test, testCount, stateEngine)
						
					# Run the test
					try:
						actionValues = stateEngine.run(mutator)
					
					except RedoTestException:
						raise
					
					except MemoryError:
						# Some tests cause out of memeory
						# exceptions, let skip past them
						print "Warning: Out of memory, going to next test"
						pass
					
					except OverflowError:
						# Some tests cause out of memeory
						# exceptions, let skip past them
						print "Warning: Out of memory, going to next test"
						pass
					
					except SoftException, e:
						# In the case of the first iteration we should
						# never fail.
						if testCount == 1:
							raise PeachException("Error: First test case failed: ",e)
						
						# Otherwise ignore any SoftExceptions
						# and head for next iteration
						pass
					
					# Pause as needed
					time.sleep(run.waitTime)
					
					mutator.onTestCaseFinished(test, testCount, stateEngine)
					
					# Notify
					if not countOnly:
						self.watcher.OnTestCaseFinished(run, test, testCount, actionValues)
					
					self.agent.OnTestFinished()
					
					# Should we repeat this test?
					if self.agent.RedoTest():
						print "-- Repeating test --"
						raise RedoTestException()
					
					# Check for faults
					if self.agent.DetectedFault():
						# Collect data
						print "-- Detected fault, getting data --"
						results = self.agent.GetMonitorData()
						
						mutator.onFaultDetected(test, testCount, stateEngine, results, actionValues)
						
						self.watcher.OnFault(run, test, testCount, results, actionValues)
						self.agent.OnFault()
					
					# Check for stop event
					if self.agent.StopRun():
						print "-- Detected StopRun, bailing! --"
						self.watcher.OnStopRun(run, test, testCount, None, actionValues)
						break
					
					# Increment our mutator
					mutator.next()
					
					# Reset the redoCounter
					redoCount = 0
				
				except RedoTestException, e:
					if redoCount == 3:
						raise PeachException(e.message)
					
					redoCount += 1
					testCount -= 1
				
				except PathException:
					# Ignore PathException while running tests
					
					mutator.next()
					
				except SoftException:
					mutator.next()
				
				# Have we completed our range?
				if (testRange != None and testCount > endCount) or \
					(Engine.justOne and startCount == None) or \
					(Engine.justOne and startCount == testCount):
					
					print "-- Completed our iteration range, exiting"
					break
				
				
		except MutatorCompleted:
			pass
		
		except KeyboardInterrupt:
			print "\n"
			print "-- User canceled run"
			saveState = True
			exitImmediate = True
		
		except PeachException, e:
			if e.msg.find("Unable to reconnect to Agent") > -1:
				results = {
					"_Bucket" : "AgentConnectionFailed"
				}
				
				self.watcher.OnFault(run, test, testCount, results, actionValues)
			
			raise
		
		except:
			# Always save state on exceptions
			saveState = True
			
			self.watcher.OnTestCaseException(run, test, testCount, None)
			raise
		
		finally:
			
			# Make sure any publishers are shutdown
			try:
				for pub in test.publishers:
					if hasattr(pub, "hasBeenConnected") and pub.hasBeenConnected:
						pub.close()
						pub.hasBeenConnected = False
					
					if hasattr(pub, "hasBeenStarted") and pub.hasBeenStarted:
						pub.stop()
						pub.hasBeenStarted = False
				
					pub.finalize()
			except:
				pass
				
			# We should also stop agents.
			self._stopAgents(run, test)
			
		if not countOnly:
			self.watcher.OnTestFinished(run, test)
		
		#self._stopAgents(run, test)
		return None
	
	def _runPathTest(self, run, test):
		stateMachine = test.stateMachine
		
		# If no path declaration found then simply skip the validation
		if len(stateMachine.getRoute()) == 0:
			return
		
		print ("[*] Running path validation test[%s]\n" % test.name)
		try:
			
			stateEngine = StateEngine(self, stateMachine, test.publishers)
			
			# Create a path validator to check basic validation rules
			mutator = PathValidationMutator()
			pathValidator = PathValidator(stateEngine.pathFinder, mutator)
			try:
				actionValues = stateEngine.run(mutator)
				
				print "Traced route: "
				print " - ".join(["%s" % str(stateName) for stateName in mutator.states])
				
				pathValidator.validate()
			except PathException, e:
				raise PeachException(str(e))
			
		except PeachException, e:
			print ("\n[-] End of path validation test : Validation failed!\n")
			raise e
		
		else:
			print("\n[+] End of path validation test : Successfully passed\n")
		

# ##################################################################################

import sys, os, time, pickle

from Peach.Engine.state import StateEngine
from Peach.Engine.common import *
from Peach.Engine.common import SoftException
from Peach.Engine.path import *

from Peach.agent import AgentPlexer
from Peach.mutatestrategies import *
from Peach.MutateStrategies import *

from Peach.analyzer import Analyzer
from Peach.Analyzers import *

from Peach.Mutators import *
from Peach.Mutators.path import *

# end
