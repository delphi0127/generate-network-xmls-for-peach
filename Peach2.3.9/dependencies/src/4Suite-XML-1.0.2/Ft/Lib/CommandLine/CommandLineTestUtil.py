########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Lib/CommandLine/CommandLineTestUtil.py,v 1.16 2005/04/13 23:41:04 jkloth Exp $
"""
Command-line script related extensions to the test suite framework

Copyright 2004 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

import os

import Ft

class TestRun:

    def __init__(self, name, options, args, expectedOut=None,
                 validationFunc=None, input=None, outFile=None,
                 skipOutputTest=False, compareFunc=cmp):
        self.name = name
        self.expectedOut = expectedOut
        self.validationFunc = validationFunc
        self.input = input
        self.output = outFile
        self.skipOutputTest = skipOutputTest
        self.compareFunc = compareFunc
        self.argv = self.makeCommandLine(options, args)
        return

    def makeCommandLine(self, options, args):
        argv = []

        # create the options list
        for name, value in options.items():
            if value:
                if ' ' in str(value):
                    value = '"%s"' % value
                option = '--%s=%s' % (name, value)
            else:
                option = '--%s' % name
            argv.append(option)

        # create the argument list
        for arg in args:
            if ' ' in str(arg):
                arg = '"%s"' % arg
            argv.append(arg)

        return ' '.join(argv)

    def test(self, tester, script):

        # create the display version of the commandline
        title = script + ' ' + self.argv

        # create the complete commandline
        script = os.path.join(Ft.GetConfigVar('BINDIR'), script)
        command = script + ' ' + self.argv

        tester.startGroup(self.name)
        tester.startTest(title)

        if self.skipOutputTest:
            if self.input:
                pipe = os.popen(command, 'w')
                pipe.write(self.input)
                status = pipe.close()
            else:
                pipe = os.popen(command, 'r')
                result = pipe.read()
                try:
                    status = pipe.close()
                except IOError, e:
                    status = -1
            if status is not None:
                # re-run the command capturing the output
                input, output = os.popen4(command)
                input.close()
                error = output.read()
                try:
                    output.close()
                except IOError:
                    pass
                tester.error("Error executing '%s':\n%s" % (script, error))
        else:
            # popen4 combines stdout and stderr into one stream
            input, output = os.popen4(command)

            # Send the input to the command
            if self.input:
                input.write(self.input)
            input.close()

            # Get the output from the command
            result = output.read()
            try:
                output.close()
            except IOError:
                # Windows sometimes complains
                pass

            # Use the output file instead of the stream content
            if self.output:
                f = open(self.output)
                result = f.read()
                f.close()
                os.remove(self.output)

            if result:
                if not self.expectedOut:
                    tester.warning("Unexpected output:\n%r" % result)
                else:
                    tester.compare(self.expectedOut, result,
                                   func=self.compareFunc, diff=1)
            elif self.expectedOut:
                tester.error("Missing expected output:\n%r" % self.expectedOut)

        if self.validationFunc and not self.validationFunc(tester):
            tester.error("Validation Failed")

        tester.testDone()
        tester.groupDone()
        return

class Test:

    def __init__(self, commandName, runs):
        self.commandName = commandName
        self.runs = runs
        return

    def test(self, tester):
        tester.startGroup("Command-line %r" % self.commandName)
        for run in self.runs:
            run.test(tester, self.commandName)
        tester.groupDone()

