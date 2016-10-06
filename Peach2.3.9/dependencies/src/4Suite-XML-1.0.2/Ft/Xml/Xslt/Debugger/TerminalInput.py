
import code, string
import DebugCommands

g_commandDict = {'r':DebugCommands.RUN,
                 'run':DebugCommands.RUN,
                 'q':DebugCommands.QUIT,
                 'quit':DebugCommands.QUIT,
                 't':DebugCommands.TEMPLATE,
                 'template':DebugCommands.TEMPLATE,
                 'p':DebugCommands.PRINT,
                 'print':DebugCommands.PRINT,
                 'ls':DebugCommands.LIST_SHEET,
                 'bt':DebugCommands.BACK_TRACE,
                 's':DebugCommands.STEP,
                 'step':DebugCommands.STEP,
                 'n':DebugCommands.NEXT,
                 'next':DebugCommands.NEXT,
                 'test':DebugCommands.TEST,
                 'e':DebugCommands.EVAL,
                 'eval':DebugCommands.EVAL,
                 'm':DebugCommands.MATCH,
                 'match':DebugCommands.MATCH,
                 'a':DebugCommands.AVT,
                 'avt':DebugCommands.AVT,
                 'lt':DebugCommands.LIST_TEMPLATE,
                 'break':DebugCommands.SET_BREAK,
                 'b':DebugCommands.SET_BREAK,
                 'lb':DebugCommands.LIST_BREAK,
                 'db':DebugCommands.DELETE_BREAK,
                 'h':DebugCommands.HELP,
                 'help':DebugCommands.HELP,
                 }


class TerminalInputHandler:

    def __init__(self):
        
        self.console = code.InteractiveConsole({})
        self.lastCommand = None




    def getNextCommand(self,outputHandler):

        try:
            cmd = self.console.raw_input(">>> ")
        except EOFError:
            raise SystemExit()
        


        args = ()
        index = string.find(cmd,' ')
        if index != -1:
            args = []
            args = string.split(cmd[index+1:],',')
            cmd = cmd[:index]

        if self.lastCommand and not cmd:
            cmd = self.lastCommand
        self.lastCommand = cmd

        if not g_commandDict.has_key(cmd):
            outputHandler.display_error("Unknown Command '%s'" % cmd)
            return None

        return g_commandDict[cmd],args



