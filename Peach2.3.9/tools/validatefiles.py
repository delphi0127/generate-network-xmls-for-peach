'''
This script will validate a DataModel against an collection of
input files.  It will verify they are able to be parsed correctly.
'''

import os, sys, time, glob

sys.path.append("c:/peach")

print """
]] Peach Validate Multiple Files
]] Copyright (c) Michael Eddington

"""

if len(sys.argv) < 3:
	print """
This program will crack a series of files against a selected
data model and verify the output matches the input.  This allows
for build validation of data models.

Syntax: validatefiles <Peach PIT> <Data Model> <Input Files>

  Peach PIT   - The Peach XML file containing the data model
  Data Model  - Name of the data model to crack against
  Input Files - The path to a folder or a UNIX style Glob

"""
	sys.exit(0)

from Peach.Engine import *
from Peach.Engine.incoming import DataCracker
from Peach.publisher import *
from Peach.analyzer import Analyzer
from Peach.Analyzers import *

inputFiles = []
inputFilesPath = sys.argv[3]
dataModelName = sys.argv[2]
xmlFile = sys.argv[1]

if os.path.isdir(inputFilesPath):
	for file in os.listdir(inputFilesPath):
		inputFiles.append(os.path.join(inputFilesPath, file))

else:
	inputFiles = glob.glob(inputFilesPath)

print " - Found %d files\n" % len(inputFiles)

peach = Analyzer.DefaultParser().asParser("file:"+xmlFile)
dataModel = peach.templates[dataModelName]

for file in inputFiles:
	#peach = Analyzer.DefaultParser().asParser("file:"+xmlFile)
	dataModel = peach.templates[dataModelName].copy(peach)
	
	fd = open(file, "rb")
	data = fd.read()
	fd.close()
	
	buff = PublisherBuffer(None, data, True)
	
	cracker = DataCracker(peach)
	cracker.optmizeModelForCracking(dataModel, True)
	cracker.crackData(dataModel, buff)
	
	if dataModel.getValue() == data:
		print "Cracking of file '"+file+"' passed."
	else:
		print "Cracking of file '"+file+"' failed."

print "Done\n"

# end
