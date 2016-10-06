

RUN = 1
QUIT = 2
PRINT = 3
TEMPLATE = 4
LIST_SHEET = 5
BACK_TRACE=6
STEP = 7
NEXT = 8
TEST = 9
EVAL = 10
MATCH = 11
AVT = 12
LIST_TEMPLATE = 13
SET_BREAK = 14
LIST_BREAK = 15
DELETE_BREAK = 16

HELP = 100

g_runCommands = [RUN,
                 TEMPLATE,
                 STEP,
                 NEXT,
                 ]



class ExitException:
    pass
