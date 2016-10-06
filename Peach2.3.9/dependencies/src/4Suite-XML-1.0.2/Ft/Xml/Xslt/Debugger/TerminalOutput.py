########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/Xslt/Debugger/TerminalOutput.py,v 1.5 2004/04/16 06:27:48 mbrown Exp $
"""
Output handler to route debugger messages to a terminal

Copyright 2004 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

import cStringIO, string, sys, traceback
from Ft.Xml.Xslt import Processor
from xml.dom import Node
import DebugCommands
from Ft.Xml.XPath import NAMESPACE_NODE
from Ft.Lib import boolean



import types,urllib
try:
    g_stringTypes= [types.StringType, types.UnicodeType]
except:
    g_stringTypes= [types.StringType]



g_commandPrint = {DebugCommands.RUN:'Run',
                  DebugCommands.QUIT:'Quit',
                  DebugCommands.PRINT:'Print',
                  DebugCommands.TEMPLATE:'Run to Template',
                  DebugCommands.LIST_SHEET:'List Sheet',
                  DebugCommands.BACK_TRACE:'Back Trace',
                  DebugCommands.STEP:'Step',
                  DebugCommands.NEXT:'Next',
                  DebugCommands.EVAL:'Evaluate Expression',
                  DebugCommands.TEST:'Test XPath',
                  DebugCommands.MATCH:'Match Pattern',
                  DebugCommands.AVT:'Attribute Value Template',
                  DebugCommands.LIST_TEMPLATE:'List current Template',
                  DebugCommands.SET_BREAK:'Set a break point in stylesheet',
                  DebugCommands.DELETE_BREAK:'Delete a break point in stylesheet',
                  DebugCommands.LIST_BREAK:'List break points',
                  DebugCommands.HELP:'help',
                  }

g_help = {'run':"Run till the next break point",
          'quit':"Exit the program",
          'print':"Print information about the context",
          'template':"Run till the next template is instantiated",
          'ls':"List the current stylesheet",
          'bt':"Print the call stack",
          'step':"Step to next element",
          'next':"Step to next element at same level",
          'eval':"Evaluate a XPath expression at the current context",
          'test':"Evaluate a XPath expression at the current context and return the boolean results",
          'match':"Evaluate a XPattern expression at the current context",
          'avt':"Evaluate a attribute value template at the current context",
          'lt':"Print the current template",
          'b':'Set a break point in stylesheet',
          'db':'Delete a break point in stylesheet',
          'lb':'List break points',
          'help':'help',
          }


g_detailedHelp = g_help.copy()

g_detailedHelp['print'] = """Print arg

  Possible values for arg:
    con
          The current context
    con.position
          The position of the current context
    con.size
          The size of the current context
    con.node
          The node of the current context
    con.mode
          The mode of the current context
    con.currentNode
          The current node of the current context
    $
          The last XPath results evaluated
    $$
          The last results from a XSLT element instantiation
"""

g_detailedHelp['ls'] = """List Sheet

  ls [fileName:][start[-end]]

    fileName:  Name of stylesheet to list, default to the current sheet
    start:     Line number to start listing at.T
                 The default is one line before the current line
    end:       The last line to print.
                 The default is nine lines after the current line


"""

class TerminalOutputHandler:



    def display_error(self,err):
        sys.stderr.write(err+'\n')
    def display(self,msg):
        print msg

    def display_exception(self,etype,value,tb):
        traceback.print_exception(etype, value, None)


    def display_expressionResults(self,expr,rt):
        print expr + " --> " + str(rt)

    def display_backTrace(self,tb):
        indent = ""
        for t in tb[1:]:
            n = self._getPrettyNodeName(t)
            if hasattr(t,'nodeType'):
                fileName = t.baseUri
                lineNum = str(t._ft_lineNumber)
                n = n + ' (%s line %d)' % (t.baseUri,t._ft_lineNumber)

            print indent + n
            indent = indent + "  "

    def display_breakpoints(self,bps):
        for bNum,lineNum,fileName in bps:
            print "Break Point %d: File: %s Line Number: %d" % (bNum,fileName,lineNum)



    def display_selectResults(self,expr,rt):
        print expr + " -->",
        object_type = type(rt)
        if hasattr(rt, 'nodeType'):
            self._printNode(rt)
        elif object_type in g_stringTypes:
            print rt
        elif object_type in [types.IntType, types.LongType]:
            print rt
        elif isinstance(rt, types.FloatType):
            if str(rt) == 'nan':
                print 'NaN'
            else:
                print "%g"%(rt)
        elif isinstance(rt, boolean.BooleanType):
            print str(rt)
        elif isinstance(rt, types.ListType):
            print
            for r in rt:
                print self._getPrettyNodeName(r)
        print "-" * 15



    def display_context(self,context):

        print "Current Context"
        print "-"*15
        print "Node: %s" % str(context.node)
        print "Position: %d" % context.position
        print "Size: %d" % context.size
        print "Current Node: %s" % str(context.currentNode)
        print "Var Bindings: %s" % str(context.varBindings)
        print "Processor Nss: %s" % str(context.processorNss)
        print "Mode: %s" % str(context.mode)

    def display_contextPosition(self,position):
        print "Context Position: %d" % position

    def display_contextSize(self,size):
        print "Context Size: %d" % size

    def display_contextMode(self,mode):
        print "Context Mode: %s" % mode


    def display_contextNode(self,node):
        print "Context.Node: "
        self._printNode(node)

    def display_contextCurrentNode(self,cn):
        print "Context.CurrentNode: "
        self._printNode(cn)


    def display_lastResult(self,lr):
        print "Last Results"
        print "-"*10
        print lr
        print "-"*10

    def display_lastOutputs(self,lo):
        print "Outputs"
        print "-"*10
        indent = ""
        for name,args in lo:
            if name == 'Start: element':
                print indent,
                print "<%s>" % args['name']
                indent = indent + "  "
            elif name == 'Start: document':
                print indent,
                print "<?xsml version='1.0'?>"
                indent = indent + "  "
            elif name == "End: element":
                indent = indent[:-2]
                print indent,
                print "</>"
            elif name == 'text':
                print indent,
                print string.strip(args['text'])
            elif name == 'attribute':
                print indent,
                print "%s='%s'" % (args['name'],args['value'])
            else:
                print name,args


        print "-"*10


    def display_currentPosition(self,node):
        print

        if isinstance(node,Processor.Processor):
            print "-"*40
            print "Processor.ApplyTemplates"
        elif hasattr(node,'nodeType'):
            #Print the line number +/- 3
            marker = 6 + node._ft_columnNumber + 1
            print '-'*marker + "|" + '-' * (40-marker)
            print ' '*marker + "V"

            self._printFromFile(node.baseUri,node._ft_lineNumber,2,2)
        else:
            return str(node)
        print "-"*40


    def display_currentCommand(self,cmd):
        print g_commandPrint[cmd]


    def _printNode(self,node):
        if hasattr(node,'baseUri'):
            self._printFromFile(node.baseUri,node._ft_lineNumber,1,9)
        elif hasattr(node,'nodeType'):
            st = cStringIO.StringIO()
            PrettyPrint(node,stream=st)
            print st.getvalue()
        elif isinstance(node,Processor.Processor):
            print "Processor"
        else:
            print str(node)

    display_node = _printNode


    def display_sheet(self,node,start=None,end=None,fileName=None):

        if isinstance(node,Processor.Processor) and fileName is None:
            print "Processor"
            return

        if fileName is None:
            if hasattr(node,'baseUri'):
                fileName = node.baseUri
            else:
                raise Exception("You need to specify a fileName")

        if start is None:
            if hasattr(node,'_ft_lineNumber'):
                start = node._ft_lineNumber
            else:
                start = 1

        if end is None:
            end = 9
        else:
            end = end - start

        self._printFromFile(fileName,start,1,end)


    def _getPrettyNodeName(self,node):
        if isinstance(node,Processor.Processor):
            return "Processor.ApplyTemplates"
        elif hasattr(node,'nodeType'):
            if node.nodeType == Node.ELEMENT_NODE:
                st = "<%s " % node.nodeName
                for attr in node.attributes:
                    st = st + "%s ='%s' " % (attr.name,attr.value)
                return st[:-1] + '>'
            else:
                return str(node)
        else:
            return str(node)

    g_fileLineCache = {}
    def _printFromFile(self,fileName,lineNo,previousLines,extraLines,addMarker = 1):
        if not self.g_fileLineCache.has_key(fileName):
            lines = Uri.UrlOpen(fileName).readlines()
            self.g_fileLineCache[fileName] = lines
        else:
            lines = self.g_fileLineCache[fileName]


        start = lineNo-previousLines-1
        if start < 0:
            start = 0
        ctr = start

        for line in lines[start:lineNo+extraLines]:
            if addMarker and ctr == lineNo-1:
                marker = "->"
            else:
                marker = "  "
            print "%03d%s: %s" % (ctr+1,marker,line[:-1])
            ctr = ctr + 1

    def display_help(self,args):

        if not args:
            commands = g_help.keys()
            commands.sort()
            print "4XDebug Commands"
            for cmd in commands:
                print "%s: %s" % (cmd,g_help[cmd])
        else:
            print g_detailedHelp.get(args[0],"Unknown Command %s" % args[0])
