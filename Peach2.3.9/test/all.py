'''
Run all of the unit tests
'''

import warnings, exceptions
## Note: this will disable all deprication warnings!  For v2.6 compat.
warnings.filterwarnings('ignore', message='', category=exceptions.DeprecationWarning)

import sys

#if sys.version.find("AMD64") > -1:
#	PSYCO = False
#else:
#	PSYCO = True
#
#if PSYCO:
#	import psyco
#	psyco.full()

# 1. Add your module to this import list

import analyzers
import path
import offset
import fixups
import mutators
import misc
import incoming
import relations
import publishers
import template
import transformers
import state
import flags
import data
import state
import blobs
import numberz
import strings
import parsing
import unittest
import os, coverage, coverage_color

# 2. Add your module to this array

allModules = [
	analyzers,
	#path,
	offset,
	fixups,
	incoming,
	relations,
	publishers,
	template,
	transformers,
	state,
	flags,
	data,
	blobs,
	numberz,
	strings,
	# These are slow and should be last.
	#mutators,
	misc
	]

def suite():
	suites = []
	for m in allModules:
		suites.append(m.suite())
	
	return unittest.TestSuite(suites)

if __name__ == "__main__":
	COVERAGE_DIR = "coverage" # Where the HTML output should go
	COVERAGE_MODULES = ["Peach",
						"Peach.Engine.parser",
						"Peach.Engine.engine",
						"Peach.Engine.incoming",
						"Peach.Engine.dom",
						"Peach.Engine.state"
						] # The modules that you want colorized
	runner = unittest.TextTestRunner()
	coverage.start()
	runner.run(suite())
	coverage.stop()
	if not os.path.exists(COVERAGE_DIR):
		os.makedirs(COVERAGE_DIR)
	for module_string in COVERAGE_MODULES:
		module = __import__(module_string, globals(), locals(), [""])
		f,s,m,mf = coverage.analysis(module)
		fp = file(os.path.join(COVERAGE_DIR, module_string + ".html"), "wb")
		coverage_color.colorize_file(f, outstream=fp, not_covered=mf)
		fp.close()
	coverage.erase()

# end
