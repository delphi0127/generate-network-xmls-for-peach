'''
Misc test cases
'''

import unittest
import utils, helpers
from struct import pack, unpack
from Peach.Mutators import *
from Peach.Engine.engine import *
import utils, helpers

def suite():
	suite = unittest.TestSuite()
	suite.addTest(PngTestCase())
	suite.addTest(MiscRef1TestCase())
	suite.addTest(SwfTestCase())
	#suite.addTest(SwfCountTestCase())
	#suite.addTest(PngCountTestCase())
	return suite

class PngTestCase(utils.PeachTcpTestCase):
	'''
	This unittest verifies a number of different things including, but not limited to:
	
	  - Long hex values in Blobs
	  - C style hex format
	  - Block inheritence
	  - Block inheritence w/override
	  - Fixup
	  - Relations
	  - Relations with inheritence w/override
	  
	'''
	def runTest(self):
		# Test
		self.peachUtils.RunPeachXml("miscPng.xml")
		ret = self.peachUtils.GetListenerData()
		fd = open("miscPng.bin", "rb+")
		data = fd.read()
		fd.close()
		assert ret == data, 'miscPng.xml failed.'

class SwfTestCase(utils.PeachTcpTestCase):
	def runTest(self):
		# Test
		self.peachUtils.RunPeachXml("miscSwf.xml")
		ret = self.peachUtils.GetListenerData()
		fd = open("miscSwf.bin", "rb+")
		data = fd.read()
		fd.close()
		assert ret == data, 'miscSwf.xml failed.'

class SwfCountTestCase(utils.PeachTestCaseNoAgent):
	def runTest(self):
		
		parse = ParseTemplate()
		peach = parse.parse("file:miscSwf2.xml")
		
		test = peach["DefaultRun"].tests[0]
		
		stateMachine = test.stateMachine
		stateEngine = StateEngine(peach["DefaultRun"], stateMachine, test.publisher)
		
		mutators = []
		for m in test.getMutators():
			mutators.append(m.mutator)
		
		mutator = MutatorCollection(mutators)
		
		print "Running %d iterations" % (len(mutators)+1)
		for i in range(len(mutators)+1):
			print ".",
			# Run state machine
			mutator.getCount()
			stateEngine.run(mutator)
			mutator.next()
		
		# now get values!
		print "\nWaiting for count"
		timeout = 200
		goNext = False
		count = 0
		for i in range(timeout):
			mutator.getCount()
			print ".",
			time.sleep(1)
			
			count = 0
			goNext = False
			for m in mutators:
				m.onStateMachineComplete(None)
				if m.getCount() == -1:
					print "%s did not have count yet" % m.name
					goNext = True
					#break
				
				count += m.getCount()
			
			if goNext:
				continue
			
			break
		
		print ""
		for m in mutators:
			print "%s:" % m.name, m.getCount()
		
		print "\nTotal Count:", count
		
		assert not goNext, "Not everything counted okay"
		
		assert count == 88994, "Count did not match, %d != %d" % (count, 88994)

class PngCountTestCase(utils.PeachTestCaseNoAgent):
	def runTest(self):
		
		parse = ParseTemplate()
		peach = parse.parse("file:miscPng2.xml")
		
		test = peach["DefaultRun"].tests[0]
		
		stateMachine = test.stateMachine
		stateEngine = StateEngine(peach["DefaultRun"], stateMachine, test.publisher)
		
		mutators = []
		for m in test.getMutators():
			mutators.append(m.mutator)
		
		mutator = MutatorCollection(mutators)
		
		print "Running %d iterations" % (len(mutators)+1)
		for i in range(len(mutators)+1):
			print ".",
			# Run state machine
			mutator.getCount()
			stateEngine.run(mutator)
			mutator.next()
		
		# now get values!
		print "\nWaiting for count"
		timeout = 200
		goNext = False
		count = 0
		for i in range(timeout):
			mutator.getCount()
			print ".",
			time.sleep(1)
			
			count = 0
			goNext = False
			for m in mutators:
				m.onStateMachineComplete(None)
				if m.getCount() == -1:
					print "%s did not have count yet" % m.name
					goNext = True
					#break
				
				count += m.getCount()
			
			if goNext:
				continue
			
			break
		
		print ""
		for m in mutators:
			print "%s:" % m.name, m.getCount()
		
		print "\nTotal Count:", count
		
		assert not goNext, "Not everything counted okay"
		
		assert count == 56232, "Count did not match, %d != %d" % (count, 56232)

class MiscRef1TestCase(utils.PeachTestCaseNoAgent):
	def runTest(self):
		xmlFile = "file:miscRef1.xml"
		watcher = helpers.UnittestEngineWatcher()
		engine = Engine()
		engine.Run(xmlFile, None, False, watcher)
	
	def countTestCases(self):
		return len(utils.Utils.mutators)



if __name__ == "__main__":
    unittest.main()

# end
