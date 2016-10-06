'''
Several testcases around mutators
'''

import sys, getopt
sys.path.append("..")
import unittest
import utils, helpers

from Peach.Mutators import *
from Peach.Engine.engine import *

utils.Utils.mutators = [
	"default.NullMutator",
	"string.StringTokenMutator",
	"string.XmlW3CMutator",
	"string.PathMutator",
	"string.HostnameMutator",
	"string.FilenameMutator",
	"number.NumericalEdgeCaseMutator",
	"number.NumericalVarianceMutator",
	"number.FiniteRandomNumbersMutator",
	"blob.BitFlipperMutator",
	"datatree.DataTreeRemoveMutator",
	"datatree.DataTreeDuplicateMutator",
	"datatree.DataTreeSwapNearNodesMutator"
	#"array.ArrayVaranceMutator",
	#"array.ArrayNumericalEdgeCasesMutator",
	#"array.ArrayReverseOrderMutator",
	#"array.ArrayRandomizeOrderMutator",
	#"size.SizedVaranceMutator",
	#"size.SizedNumericalEdgeCasesMutator",
	]

def suite():
	suite = unittest.TestSuite()
	suite.addTest(MutatorsCountTest())
	suite.addTest(MutatorsGetState())
	suite.addTest(MutatorsRunSingle())
	suite.addTest(MutatorsRunCombo())
	suite.addTest(MutatorSize())
	
	return suite


class MutatorsCountTest(utils.PeachTestCaseNoAgent):
	def runTest(self):
		
		parse = ParseTemplate()
		peach = parse.parse("file:mutatorsCombo.xml")
		
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


class MutatorsGetState(utils.PeachTestCaseNoAgent):
	def runTest(self):
		
		parse = ParseTemplate()
		peach = parse.parse("file:mutatorsCombo.xml")
		
		test = peach["DefaultRun"].tests[0]
		
		stateMachine = test.stateMachine
		stateEngine = StateEngine(peach["DefaultRun"], stateMachine, test.publisher)
		
		mutators = []
		for m in test.getMutators():
			mutators.append(m.mutator)
			state = m.mutator.getState()
			m.mutator.setState(state)
		
		mutator = MutatorCollection(mutators)
		
		print "Running %d iterations" % (len(mutators)+1)
		for i in range(len(mutators)+1):
			print ".",
			# Run state machine
			mutator.getCount()
			stateEngine.run(mutator)
			mutator.next()
		
		for m in mutators:
			state = m.getState()
			m.setState(state)
			
		mutator = MutatorCollection(mutators)
		print "\nRunning %d iterations" % (len(mutators)+1)
		for i in range(len(mutators)+1):
			print ".",
			# Run state machine
			stateEngine.run(mutator)
			mutator.next()
		

##class MutatorsRunMultiple(utils.PeachTestCaseNoAgent):
##	def runTest(self):
##		for m in utils.Utils.mutators:
##			m = m[m.index('.')+1:]
##			xmlFile = "file:mutatorsMultiple%s.xml" % m
##			
##			print "\nRunning: %s" % xmlFile
##			watcher = helpers.UnittestEngineWatcher()
##			engine = Engine()
##			engine.Run(xmlFile, None, False, watcher)
##	
##	def countTestCases(self):
##		return len(utils.Utils.mutators)
##
###class MutatorsRunSingle(utils.PeachTestCaseNoAgent):
###	def runTest(self):
###		xmlFile = "file:mutatorsSingleFiniteRandomNumbersMutator.xml"
###		
###		print "\nRunning: %s" % xmlFile
###		watcher = helpers.UnittestEngineWatcher()
###		engine = Engine()
###		engine.Run(xmlFile, None, False, watcher)
###	
###	def countTestCases(self):
###		return len(utils.Utils.mutators)

class MutatorSize(utils.PeachTestCaseNoAgent):
	def runTest(self):
		xmlFile = "file:mutatorSize.xml"
		
		print "\nRunning: %s" % xmlFile
		watcher = helpers.UnittestEngineWatcher()
		engine = Engine()
		engine.Run(xmlFile, None, False, watcher)
	
	def countTestCases(self):
		return len(utils.Utils.mutators)

class MutatorsRunSingle(utils.PeachTestCaseNoAgent):
	def runTest(self):
		for m in utils.Utils.mutators:
			m = m[m.index('.')+1:]
			xmlFile = "file:mutatorsSingle%s.xml" % m
			
			print "\nRunning: %s" % xmlFile
			watcher = helpers.UnittestEngineWatcher()
			engine = Engine()
			engine.Run(xmlFile, None, False, watcher)
	
	def countTestCases(self):
		return len(utils.Utils.mutators)

class MutatorsRunCombo(utils.PeachTestCaseNoAgent):
	def runTest(self):
		xmlFile = "file:mutatorsCombo.xml"
		
		print "\nRunning: %s" % xmlFile
		watcher = helpers.UnittestEngineWatcher()
		engine = Engine()
		engine.Run(xmlFile, None, False, watcher)


if __name__ == "__main__":
    unittest.main()

# end

#
#- Run all mutators all the way through
#  - Single type element
#  - Multiple type elements
#  - Combo file
#- Count all mutators
#- Memory leak detection on long run
#- Run each through, snapshot results for comparison
#  - Run compare tests
#
