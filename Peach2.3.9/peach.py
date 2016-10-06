#!/usr/bin/python

'''
Peach 2 Console Runtime

This is the Peach Runtime.  The Peach Runtime is one of the many ways
to use Peach XML files.  Currently this runtime is still in development
but already exposes several abilities to the end-user such as performing
simple fuzzer runs, converting WireShark captures into Peach XML and
performing parsing tests of Peach XML files.

@author: Michael Eddington
@version: $Id: peach.py 2414 2011-06-24 14:11:54Z meddingt $
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

# $Id: peach.py 2414 2011-06-24 14:11:54Z meddingt $

import sys, os, time

# Add our root to the python path
if not (hasattr(sys,"frozen") and sys.frozen == "console_exe"):
	sys.path.append(sys.path[0])
else:
	p = os.path.dirname(os.path.abspath(sys.executable))
	sys.path.append(p)
	sys.path.append( os.path.normpath( os.path.join(p, "..") ) )

import getopt, os, warnings,exceptions
sys.path.append(".")

## Note: this will disable all deprication warnings!  For v2.6 compat.
warnings.filterwarnings('ignore', message='', category=exceptions.DeprecationWarning)

try:
	import Ft
except:
	print "\nError loading 4Suite XML library.  This library"
	print "can be installed from the dependencies folder or"
	print "downloaded from http://4suite.org/.\n\n"
	sys.exit(0)
 

# Note: this is required for multiprocessing module to work.
if __name__ == '__main__':
		
	import sys
	import atexit
	
	def atexit_handler():
		try:
			# We want to flush the log file
			from Peach.Engine import engine
			engine.Engine.context.watcher.watchers[-1].OnCrashOrBreak()
		except:
			pass
	atexit.register(atexit_handler)
	
	try:
		from multiprocessing import freeze_support
		freeze_support()
	except:
		pass

	def printError(str):
		sys.stderr.write("%s\n" % str)
	
	def usage():
		printError("""
This is the Peach Runtime.  The Peach Runtime is one of the many ways
to use Peach XML files.  Currently this runtime is still in development
but already exposes several abilities to the end-user such as performing
simple fuzzer runs, converting WireShark captures into Peach XML and
performing parsing tests of Peach XML files.

Please submit any bugs to Michael Eddington <mike@phed.org>.

Syntax:

  peach -a [port] [password]
  peach -c peach_xml_file [run_name]
  peach -g
  peach [--skipto #] peach_xml_file [run_name]
  peach -p 10,2 [--skipto #] peach_xml_file [run_name]
  peach --range 100,200 peach_xml_file [run_name]
  peach -t peach_xml_file

  -1                         Perform a single iteration
  -a,--agent                 Launch Peach Agent
  -c,--count                 Count test cases
  -t,--test xml_file         Test parse a Peach XML file
  -p,--parallel M,N          Parallel fuzzing.  Total of M machines, this
							 is machine N.
  --debug                    Enable debug messages. Usefull when debugging
							 your Peach XML file.  Warning: Messages are very
							 cryptic sometimes.
  --skipto N                 Skip to a specific test #.  This replaced -r
							 for restarting a Peach run.
  --range N,M                Provide a range of test #'s to be run.
  --seed N                   Seed to use for Random strategies
  --analyzer=CLASS           Use analyzer via command line
  --parser=CLASS             Use a custom parser analyzer (replaces default XML parser)

Peach Agent

  Syntax: peach -a
  Syntax: peach -a port
  Syntax: peach -a port password
  
  Starts up a Peach Agent instance on this current machine.  Defaults to
  port 9000.  When specifying a password, the port # must also be given.

  Note: Local agents are started automatically.

Performing Fuzzing Run

  Syntax: peach peach_xml_flie [run_name]
  Syntax: peach --skipto 1234 peach_xml_flie [run_name]
  Syntax: peach --range 100,200 peach_xml_flie [run_name]
  
  A fuzzing run is started by by specifying the Peach XML file and the
  name of a run to perform.
  
  If a run is interupted for some reason it can be restarted using the
  --skipto parameter and providing the test # to start at.
  
  Additionally a range of test cases can be specified using --range.

Performing A Parellel Fuzzing Run

  Syntax: peach -p 10,2 peach_xml_flie [run_name]

  A parallel fuzzing run uses multiple machines to perform the same fuzzing
  which shortens the time required.  To run in parallel mode we will need
  to know the total number of machines and which machine we are.  This
  information is fed into Peach via the "-p" command line argument in the
  format "total_machines,our_machine".

Validate Peach XML File

  Syntax: peach -t peach_xml_file
  
  This will perform a parsing pass of the Peach XML file and display any
  errors that are found.

Debug Peach XML File

  Syntax: peach -1 --debug peach_xml_file
  
  This will perform a single iteration (-1) of your pit file while displaying
  alot of debugging information (--debug).  The debugging information was
  origionally intended just for the developers, but can be usefull in pit
  debugging as well.

""")
		sys.exit(0)
	
	printError("\n] Peach 2.3.9 DEV Runtime")
	printError("] Copyright (c) Michael Eddington\n")
	
	if sys.version[:3] not in ['2.5', '2.6', '2.7']:
		printError("Error: Peach requires Python v2.5, v2.6, or v2.7.")
		sys.exit(0)
	
	noCount = False
	verbose = False
	webWatcher = False
	restartFuzzer = False
	restartFuzzerFile = None
	parallel = None
	startNum = None
	SEED = time.time()
		
	try:
		(optlist, args) = getopt.getopt(sys.argv[1:], "p:vstcwagr:1", ['strategy=','analyzer=', 'parallel=',
																	 'restart=', 'parser=',
																	 'test', 'count', 'web', 'agent',
																	 'gui', 'debug', 'new', 'skipto=',
																	 'range', 'seed='])
	except:
		usage()
	
	if len(optlist) < 1 and len(args) < 1:
		usage()
	
	for i in range(len(optlist)):
		if optlist[i][0] == '--analyzer':
			
			# set the analyzer to use
			from Peach.Engine.common import PeachException
			from Peach.Analyzers import *
			
			try:	
				analyzer = optlist[i][1]
				if analyzer == None or len(analyzer) == 0:
					analyzer = args[0]
				
				from Peach.Engine.common import *
				from Peach.Analyzers import *
				
				try:
					cls = eval(analyzer)
					
				except:
					try:
						parts = analyzer.split(".")
						exec("import %s" % parts[0])
						
						cls = eval(analyzer)
					except:
						raise PeachException("Error, unable to load Analyzer: %s" % (repr(sys.exc_info())))
				
				if cls.supportCommandLine:
					print "[*] Using %s as analyzer" % analyzer
					
					cls = eval("%s()" % analyzer)
					
					a = {}
					
					for i in range(0, len(args), 2):
						a[args[i]] = args[i+1]
					
					cls.asCommandLine(a)
				
				elif cls.supportParser:
					print "[*] Using %s as parser" % analyzer
					Analyzer.DefaultParser = cls
				
				else:
					print "Error, analyzer does not support command line usage.\n"
			
			except PeachException, pe:
				print ""
				print "Error loading analyzer:", pe.msg, "\n"
				
			sys.exit(0)
		
		elif optlist[i][0] == '--parser':
			
			# set the analyzer to use
			
			try:	
				analyzer = optlist[i][1]
				if analyzer == None or len(analyzer) == 0:
					analyzer = args[0]
				
				from Peach.Engine.common import PeachException
				from Peach.Engine.common import *
				from Peach.Analyzers import *
				
				try:
					cls = eval(analyzer)
					
				except:
					try:
						parts = analyzer.split(".")
						exec("import %s" % parts[0])
						
						cls = eval(analyzer)
					except:
						raise PeachException("Error, unable to load Analyzer: %s" % (repr(sys.exc_info())))
				
				if cls.supportParser:
					print "[*] Using %s as parser" % analyzer
					Analyzer.DefaultParser = cls
				
				else:
					raise PeachException("Error: Analyzer %s does not support being a parser!" % analyzer)
			
			except PeachException, pe:
				print ""
				print pe.msg, "\n"
				
			sys.exit(0)
		
		elif optlist[i][0] == '--strategy':
			
			# Set the fuzzing strategy to use
			
			print ""
			print "Error, The --strategy paramter has been depricated.  Please specify the "
			print "strategy in the <Test> element via the <Strategy> child element."
			print ""
			print "Example:"
			print "  <Test name=\"TheTest\">"
			print "     <Strategy class=\"rand.RandomMutationStrategy\" />"
			print ""
			print "     <!-- ... -->"
			print "  </Test>"
			print ""
			sys.exit(0)
			
		elif optlist[i][0] == '--seed':
				SEED = optlist[i][1]
				print "[*] Using SEED: '%s'" % SEED
				
				
		elif optlist[i][0] == '--debug':
			
			# show debugging messages
			
			from Peach.Engine import *
			from Peach.Engine.common import *
			
			engine.Engine.debug = True
			
		elif optlist[i][0] == '--new':
			
			# use the new match relation stuffs
			
			from Peach.Engine import *
			from Peach.Engine.common import *
			
			engine.Engine.relationsNew = True
			
		elif optlist[i][0] == '-1':
			
			# use the new match relation stuffs
			
			from Peach.Engine import *
			from Peach.Engine.common import *
			
			print "[*] Performing single iteration"
			engine.Engine.justOne = True
			
		elif optlist[i][0] == '--range':
			
			# use the new match relation stuffs
			
			from Peach.Engine import *
			from Peach.Engine.common import *
			
			try:
				range = args[0].split(',')
				range[0] = long(range[0])
				range[1] = long(range[1])
				args = args[1:]
			except:
				range = [long(args[0]), long(args[1])]
				args = args[2:]
			
			if range[0] < 0:
				print "Error: Count must be positive."
				sys.exit(0)
			
			if range[0] >= range[1]:
				print "Error: Range must be 1 or larger."
				sys.exit(0)
				
			print "[*] Performing tests %d -> %d" % (range[0], range[1])
			engine.Engine.testRange = range
			
		elif optlist[i][0] == '--test' or optlist[i][0] == '-t':
	
			# do a parse test
			
			from Peach.Engine import *
			from Peach.Engine.common import *
			
			try:
				
				# do the test
				if args[0][:5] != 'file:':
					args[0] = 'file:' + args[0]
				
				from Peach.analyzer import Analyzer
				
				parser = Analyzer.DefaultParser()
				parser.asParser(args[0])
				
				print "File parsed without errors.\n\n"
	
			except PeachException, pe:
				print ""
				print pe.msg
			
			except Ft.Xml.ReaderException, e:
				print ""
				print "An error occured parsing the XML file\n" + str(e)
			
			except:
				raise
			
			sys.exit(0)
			
		elif optlist[i][0] == '--count' or optlist[i][0] == '-c':
			
			# count the total test case #
			
			from Peach.Engine import *
			from Peach.Engine.common import *
			
			if args[0][:5] != 'file:':
				args[0] = 'file:' + args[0]
			
			engine = engine.Engine()
			if len(args) > 1:
				engine.Count(args[0], args[1])
			else:
				engine.Count(args[0], None)
			
			sys.exit(0)
		
		elif optlist[i][0] == '-w' or optlist[i][0] == '--web':
			
			# enable web watcher
			
			webWatcher = True
			
		elif optlist[i][0] == '-r' or optlist[i][0] == '--restart':
			
			# Restarting a fuzzer run
			
			print "Error, -r/--restart is no longer supported.  Instead say \"--skipto N\" where N is the test count."
			sys.exit(0)
			
		elif optlist[i][0] == '--skipto':
			
			# Skip to a specific test #
			
			startNum = int(optlist[i][1])
			
		elif optlist[i][0] == '-p' or optlist[i][0] == '--parallel':
			
			# Parallel fuzzing run
			
			try:
				parallel = optlist[i][1].split(',')
				parallel[0] = long(parallel[0])
				parallel[1] = long(parallel[1])
			except:
				parallel = [long(optlist[i][1]), long(args[0])]
				args = args[1:]
			
			if parallel[0] < 1:
				print "Error: Machine count must be >= 2."
				sys.exit(0)
			
			if parallel[0] <= parallel[1]:
				print "Error: When performing parallel fuzzing run, the total number of machines must be less than the current machine."
				sys.exit(0)
			
			print "-- Parallel total machines: %d" % parallel[0]
			print "-- Parallel our machine...: %d\n" % parallel[1]
			
		elif optlist[i][0] == '-a' or optlist[i][0] == '--agent':
			
			from Peach.Engine import *
			from Peach.Engine.common import *
			
			# start a peach agent
			port = 9000
			password = None
			try:
				port = int(args[0])
				if len(args[1]) > 0:
					password = args[1]
			except:
				pass
			
			from Peach.agent import Agent
			agent = Agent(password, port)
			sys.exit(0)
			
		elif optlist[i][0] == '-v':
			verbose = True
		
		else:
			usage()
	
	from Peach.Engine import *
	from Peach.Engine.common import *
	
	engine = engine.Engine()
	engine.SEED = SEED
	watcher = None
	
	try:
		try:
			if args[0][:5] != 'file:':
				args[0] = 'file:' + args[0]
		except:
			raise PeachException("Error, did you supply the Peach Pit file?")
		
		if webWatcher == True:
			from Peach.Engine.webwatcher import PeachWebWatcher
			watcher = PeachWebWatcher()
		
		if len(args) > 1:
			engine.Run(args[0], args[1], verbose, watcher, restartFuzzerFile, noCount, parallel, startNum)
		
		else:
			engine.Run(args[0], None, verbose, watcher, restartFuzzerFile, noCount, parallel, startNum)
	
	except PeachException, pe:
		print "\n",pe.msg,"\n"
	
	except Ft.Xml.ReaderException, e:
		print ""
		print "An error occured parsing the XML file\n" + str(e)
	
	except:
		raise
	
	finally:
		if DomBackgroundCopier.copyThread != None:
			DomBackgroundCopier.stop.set()
			DomBackgroundCopier.needcopies.set()
			DomBackgroundCopier.copyThread.join()
			DomBackgroundCopier.copyThread = None


# end
