########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Lib/CommandLine/Arguments.py,v 1.4 2005/04/13 23:41:04 jkloth Exp $
"""
Classes that support advanced arg processing for command-line scripts

Copyright 2004 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

from CommandLineUtil import ArgumentError

REQUIRED = 1
OPTIONAL = 2
ZERO_OR_MORE = 3
ONE_OR_MORE = 4

class Argument:
    def __init__(self, name, description, validationFunc=None):
        self.name = name
        self.description = description
        self.validationFunc = validationFunc or (lambda x: x)
        return

class RequiredArgument(Argument):
    requirements = REQUIRED

    def gen_command_line(self):
        return self.name

    def validate(self,cmd,args):
        #Just the first
        if not len(args):
            raise ArgumentError(cmd,
                                "missing required argument '%s'" % self.name)
        return self.validationFunc(args[0]),args[1:]

class OptionalArgument(Argument):
    requirements = OPTIONAL

    def gen_command_line(self):
        return "[%s]" % (self.name)

    def validate(self,cmd,args):
        #Just the first, maybe
        if len(args):
            return self.validationFunc(args[0]),args[1:]
        return None,[]


class ZeroOrMoreArgument(Argument):
    requirements = ZERO_OR_MORE

    def gen_command_line(self):
        return "[%s]..." % (self.name)

    def validate(self,cmd,args):
        #We take the rest
        eaten = map(lambda x,f=self.validationFunc:f(x),args)
        return eaten,[]


class OneOrMoreArgument(Argument):
    requirements = ONE_OR_MORE
    def gen_command_line(self):
        return "%s [%s]..." % (self.name, self.name)

    def validate(self,cmd,args):
        #We take the rest
        if not len(args):
            raise ArgumentError(cmd,
                                "missing required argument '%s'" % self.name)
        eaten = map(lambda x,f=self.validationFunc:f(x),args)
        return eaten,[]



##        for cur_arg in cmd_args:
##            if cur_arg[2] == '.':
##                #A required arg
##                if not len(cl_args):
##                resArgs[cur_arg[0]] = self._translate_args(cur_arg[3],cur_arg[0],[cl_args[0]])[0]
##                cl_args = cl_args[1:]
##            elif cur_arg[2] == '?':
##                if len(cl_args):
##                    resArgs[cur_arg[0]] = self._translate_args(cur_arg[3],cur_arg[0],[cl_args[0]])[0]
##                    cl_args = cl_args[1:]
##            elif cur_arg[2] == '+':
##                if not len(cl_args):
##                    raise ArgumentError("missing required argument '%s'" % cur_arg[0])
##                resArgs[cur_arg[0]] = self._translate_args(cur_arg[3],cur_arg[0],cl_args)
##                cl_args = []

##            elif cur_arg[2] == '*':
##                resArgs[cur_arg[0]] = self._translate_args(cur_arg[3],cur_arg[0],cl_args)
##                cl_args = []
##        command[2] = resArgs
##        return 1


##    def _translate_args(self,func,name,args):
##        res = []
##        for arg in args:
##            try:
##                res.append(func(arg))
##            except:
##                #import traceback
##                #traceback.print_exc()
##                raise ArgumentError('failed conversion for %s (%s)' % (arg, name))
##        return res
