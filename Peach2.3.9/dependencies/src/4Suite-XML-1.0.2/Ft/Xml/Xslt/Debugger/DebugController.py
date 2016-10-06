import sys, string, cStringIO
import traceback
#from Ft.Xml.Xslt import Processor
from Ft.Xml.Xslt import XsltContext, parser
from Ft.Xml.Xslt import AttributeValueTemplate, TemplateElement
from Ft.Xml.XPath import Conversions, NAMESPACE_NODE, CompiletimeException, RuntimeException
import Ft.Xml.XPath


#try:
#    import readline
#except ImportError:
#    pass

import DebugCommands
import DebugWriter, TerminalInput, TerminalOutput

class DebugState:
    STOP_NEXT = 1
    RUN = 2
    STOP_TEMPLATE = 4
    STOP_END = 5
    TEST=100

class DebugController:

    def __init__(self):
        self.stack = [('Root',[])]

        self.state = DebugState.STOP_NEXT

        self.writer = DebugWriter.DebugWriter()

        self.lastResult = None

        self.lastOutputs = []

        self.breakPoints = {}

        self.callCtr = 0

        self.outputHandler = TerminalOutput.TerminalOutputHandler()
        self.inputHandler = TerminalInput.TerminalInputHandler()


    def startCall(self,element,context):

        self.callCtr = self.callCtr + 1
        self.stack.append((element,[]))
        self.context = context

        nextCmd = None

        btest = (hasattr(element,'baseUri') and (element.baseUri,element.lineNumber) in self.breakPoints.values())


        stop = ((self.state == DebugState.STOP_NEXT) or
                (self.state == DebugState.STOP_TEMPLATE and isinstance(element,TemplateElement.TemplateElement)) or
                btest
                )


        returnValue = 0
        if stop:
            if btest:
                for bNum, bValue in self.breakPoints.items():
                    if (element._4debug_fileName,element._4debug_lineNum)  == bValue:
                        break
                self.outputHandler.display("Break at #%d" % bNum)

            self.lastOutputs = self.writer.getCurrent()

            nextCmd = self.getCommand()

            #Process the next command
            if nextCmd == DebugCommands.RUN:
                self.state = DebugState.RUN
            elif nextCmd == DebugCommands.TEMPLATE:
                self.state = DebugState.STOP_TEMPLATE
            elif nextCmd == DebugCommands.STEP:
                self.state = DebugState.STOP_NEXT
            elif nextCmd == DebugCommands.NEXT:
                self.state = DebugState.STOP_END
                returnValue = DebugState.STOP_NEXT
        return returnValue

    def endCall(self,element,context,endState,result):
        self.lastResult = result
        cur = self.stack[-1]
        self.stack = self.stack[:-1]

        self.stack[-1][1].append(cur)

        if endState:
            self.state = endState

    def getCommand(self):

        self.outputHandler.display_currentPosition(self.getCurrentElement())
        while 1:


            cmd,args = self.inputHandler.getNextCommand(self.outputHandler)

            cmd = self.process(cmd,args,self)
            if cmd:
                return cmd


    def process(self,cmd,args,dc):

        self.outputHandler.display_currentCommand(cmd)

        if cmd in DebugCommands.g_runCommands:
            return cmd

        if cmd == DebugCommands.QUIT:
            raise DebugCommands.ExitException()
        elif cmd == DebugCommands.PRINT:
            #Print the context
            self.doPrint(args)
        elif cmd == DebugCommands.LIST_SHEET:
            #Print the context
            self.listSheet(args)
        elif cmd == DebugCommands.LIST_TEMPLATE:
            #Print the template
            self.listTemplate(args)
        elif cmd == DebugCommands.BACK_TRACE:
            #Print a back trace
            self.backTrace(args)
        elif cmd == DebugCommands.TEST:
            #Print a back trace
            self.test(args)
        elif cmd == DebugCommands.EVAL:
            #Print a back trace
            self.eval(args)
        elif cmd == DebugCommands.MATCH:
            #Print match on XPattern
            self.match(args)
        elif cmd == DebugCommands.AVT:
            #Eval an AVT
            self.avt(args)
        elif cmd == DebugCommands.SET_BREAK:
            #Eval an AVT
            self.setBreak(args)
        elif cmd == DebugCommands.LIST_BREAK:
            #Eval an AVT
            self.listBreak(args)
        elif cmd == DebugCommands.DELETE_BREAK:
            #Eval an AVT
            self.deleteBreak(args)
        elif cmd == DebugCommands.HELP:
            #Eval an Help
            self.help(args)
        return None


    def deleteBreak(self,args):

        if len(args) != 1:
            self.outputHandler.write("'db' requires exactly one argument\n")
            return

        try:
            bNum = int(args[0])
        except:
            self.outputHandler.display_error("Invalid integer argument %s" % str(args[0]))
            return


        if self.breakPoints.has_key(bNum):
            self.outputHandler.display("Break Point #%d deleted" % bNum)
            del self.breakPoints[bNum]
        else:
            self.outputHandler.display_error("Unknown Break Point #%d" % bNum)


    def listBreak(self,args):
        if len(args):
            self.outputHandler.display("'lb' requires exactly no argument")
            return

        self.outputHandler.display_breakpoints(map(lambda x:(x[0],x[1][1],x[1][0]),self.breakPoints.items()))


    def setBreak(self,args):
        fileName = None
        lineNum = None
        if len(args) == 1:
            #Get them
            try:
                lineNum = int(args[0])
            except:
                self.outputHandler.display_error("Invalid integer argument %s" % str(args[0]))
                return
        elif len(args) == 2:
            fileName = args[0]
            try:
                lineNum = int(args[1])
            except:
                self.outputHandler.display_error("Invalid integer argument %s" % str(args[1]))
                return
        else:
            self.outputHandler.display_error("'break' requires one or two arguments")
            return
        if fileName is None:
            if hasattr(self.getCurrentElement(),'_4debug_fileName'):
                fileName = self.getCurrentElement()._4debug_fileName
            else:
                import FtDebug.Debugger
                fileName =  FtDebug.Debugger.g_files.keys()[0]

        bps = self.breakPoints.keys()
        bps.sort()
        if len(bps) == 0:
            bNum = 0
        else:
            bNum = bps[-1] + 1
        self.outputHandler.display("Break point #%d set at line %d file %s" % (bNum,lineNum,fileName))
        self.breakPoints[bNum] = (fileName,lineNum)

    def getCurrentElement(self):
        return self.stack[-1][0]


    def backTrace(self,args):
        if len(args):
            self.outputHandler.display_error("'bt' requires exactly no argument")
            return
        tb = map(lambda x:x[0],self.stack)


        self.outputHandler.display_backTrace(tb)



    def avt(self,args):
        if not len(args):
            self.outputHandler.display_error("'avt' requires atleast one argument\n")
            return

        expr = string.join(args,',')

        con = self._copyContext(self.context)
        try:
            a = AttributeValueTemplate.AttributeValueTemplate(expr)
            rt = a.evaluate(con)
            self.outputHandler.display_expressionResults(expr,rt)
        except (CompiletimeException, RuntimeException):
            try:
                etype, value, tb = sys.exc_info()
                self.outputHandler.display_exception(etype,value,None)
            finally:
                etype = value = tb = None



    def match(self,args):
        if not len(args):
            self.outputHandler.display_error("'match' requires atleast one argument")
            return

        expr = string.join(args,',')

        con = self._copyContext(self.context)
        try:
            pattern = parser.new().parse(expr)
            rt = pattern.match(con,con.node)
            self.outputHandler.display_expressionResults(expr,rt)
        except SyntaxError:
            try:
                etype, value, tb = sys.exc_info()
                self.outputHandler.display_exception(etype,value,None)
            finally:
                etype = value = tb = None

    def test(self,args):
        if not len(args):
            self.outputHandler.display_error("'test' requires atleast one argument")
            return

        expr = string.join(args,',')
        rt = self._select(self.context,expr)
        if rt is None:
            return
        rt = Conversions.BooleanValue(rt)
        self.outputHandler.display_expressionResults(expr,rt)

    def eval(self,args):
        if not len(args):
            sys.stderr.write("'eval' requires atleast one argument\n")
            return

        expr = string.join(args,',')

        rt = self._select(self.context,expr)

        if rt is None:
            return

        self.outputHandler.display_selectResults(expr,rt)


    def _select(self,context,expr):

        #Copy the context
        con = self._copyContext(context)
        try:
            return Ft.Xml.XPath.Evaluate(expr,context = con)
        except (CompiletimeException, RuntimeException):
            try:
                etype, value, tb = sys.exc_info()
                traceback.print_exception(etype, value, None)
            finally:
                etype = value = tb = None

    def _copyContext(self,inCon):
        return XsltContext.XsltContext(inCon.node,
                                       inCon.position,
                                       inCon.size,
                                       inCon.currentNode,
                                       inCon.varBindings,
                                       inCon.processorNss,
                                       inCon.stylesheet,
                                       inCon.mode)


    def listSheet(self,args):
        fileName = None
        start = None
        end = None
        if len(args) == 1:
            #Get them
            #[fileName:]start[-end]
            fields = string.split(args[0],':')
            if len(fields) == 1:
                fileName = fields[0]
                se = None
            elif len(fields) == 2:
                fileName = fields[0]
                se = fields[1]
            else:
                self.outputHandler.display_error("Invalid argument %s" % str(args[0]))
                return
            if se is not None:
                fields = string.split(se,'-')
                if len(fields) == 1:
                    try:
                        start = int(fields[0])
                    except:
                        self.outputHandler.display_error("Invalid integer argument %s" % str(fields[0]))
                        return
                elif len(fields) == 2:
                    try:
                        start = int(fields[0])
                    except:
                        self.outputHandler.display_error("Invalid integer argument %s" % str(fields[0]))
                        return
                    try:
                        end = int(fields[1])
                    except:
                        self.outputHandler.display_error("Invalid integer argument %s" % str(fields[1]))
                        return
                else:
                    self.outputHandler.display_error("Invalid argument %s" % str(args))
                    return

        elif len(args) != 0:
            self.outputHandler.display_error("'ls' requires zero or one arguments")
            return
        self.outputHandler.display_sheet(self.getCurrentElement(),start,end,fileName)

    def listTemplate(self,args):
        if len(args):
            self.outputHandler.display("'lt' requires exactly no argument")
            return

        tb = map(lambda x:x[0],self.stack)
        tb = filter(lambda x:isinstance(x,TemplateElement.TemplateElement),tb)
        if len(tb) == 0:
            self.outputHandler.display_error("No Templates Found")
        else:
            self.outputHandler.display_node(tb[-1])

    def help(self,args):
        if len(args) > 1:
            self.outputHandler.display("'help' requires no arguments")
            return

        self.outputHandler.display_help(args)


    def doPrint(self,args):

        if len(args) != 1:
            self.outputHandler.display("'print' requires exactly one argument\n")
            return
        arg = args[0]

        #Just make it look like a python instance

        if arg == 'con':
            self.outputHandler.display_context(self.context)
        elif arg == 'con.position':
            self.outputHandler.display_contextPosition(self.context.position)
        elif arg == 'con.size':
            self.outputHandler.display_contextSize(self.context.size)
        elif arg == 'con.node':
            self.outputHandler.display_contextNode(self.context.node)
        elif arg == 'con.mode':
            self.outputHandler.display_contextMode(self.context.mode)
        elif arg == 'con.currentNode':
            self.outputHandler.display_contextCurrentNode(self.context.currentNode)
        elif arg == '$':
            self.outputHandler.display_lastResult(self.lastResult)
        elif arg == '$$':
            self.outputHandler.display_lastOutputs(self.lastOutputs)
        else:
            self.outputHandler.display_error("Unknown Variable '%s'"%arg)


