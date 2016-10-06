import sys
from Ft.Xml.Xslt import XSL_NAMESPACE
from Ft.Xml.Xslt import CategoryTypes

TEXT_NODE = (None, None)
EMPTY = -sys.maxint
ELSE = EMPTY + 1

class Atom:
    """
    Atom(arg)
    matches exactly one occurence of 'arg'
    """
    def __init__(self, token):
        self.token = token

    def buildValidator(self, validator, initial, final):
        validator.transition(self.token, initial, final)
        return
    

class Seq:
    """
    Seq(arg1, arg2, arg3...)
    matches arg1 followed by arg2 followed by arg3...
    """
    def __init__(self, *args):
        self.args = []
        for arg in args:
            if isinstance(arg, type('')):
                arg = QName(arg)
            self.args.append(arg)
        return

    def __str__(self):
        if len(self.args) > 1:
            return '(%s)' % ', '.join(map(str, self.args))
        else:
            return str(self.args[0])

    def buildValidator(self, validator, initial, final):
        s1 = initial
        for arg in self.args[:-1]:
            s2 = {}
            arg.buildValidator(validator, s1, s2)
            s1 = s2
        self.args[-1].buildValidator(validator, s1, final)
        return


class Alt:
    """
    Alt(arg1, arg2, arg3...)
    matches arg1 or arg2 or arg3...
    """

    def __init__(self, *args):
        self.args = []
        for arg in args:
            if isinstance(arg, type('')):
                arg = QName(arg)
            self.args.append(arg)
        return

    def __str__(self):
        if len(self.args) > 1:
            return '(%s)' % ' | '.join(map(str, self.args))
        else:
            return str(self.args[0])

    def buildValidator(self, validator, initial, final):
        for arg in self.args:
            arg.buildValidator(validator, initial, final)
        return


class Rep1:
    """
    Rep1(arg)
    matches one or more occurrences of 'arg'
    """
    def __init__(self, arg):
        if isinstance(arg, type('')):
            arg = QName(arg)
        self.arg = arg
        return

    def __str__(self):
        return '%s+' % str(self.arg)

    def buildValidator(self, validator, initial, final):
        state = {}
        self.arg.buildValidator(validator, initial, state)
        self.arg.buildValidator(validator, state, state)
        validator.transition(ELSE, state, final)
        return

class Opt:
    """
    Opt(arg)
    matches zero or one occurrences of 'arg'
    """

    def __init__(self, arg):
        if isinstance(arg, type('')):
            arg = QName(arg)
        self.arg = arg
        return

    def __str__(self):
        return '%s?' % str(self.arg)

    def buildValidator(self, validator, initial, final):
        self.arg.buildValidator(validator, initial, final)
        return

class Rep:
    """
    Rep(arg)
    matches zero or more occurrences of 'arg'
    """
    def __init__(self, arg):
        if isinstance(arg, type('')):
            arg = QName(arg)
        self.arg = arg
        return

    def __str__(self):
        return '%s*' % str(self.arg)

    def buildValidator(self, validator, initial, final):
        self.arg.buildValidator(validator, initial, initial)
        validator.transition(ELSE, initial, final)
        return


# special match that matches nothing
Empty = Atom(EMPTY)
Empty.__str__ = lambda : '/empty/'
Empty.__doc__ = """
Empty is the content model for childless elements
"""
Empty.__nonzero__ = lambda : 0
    
Text = Atom(TEXT_NODE)
Text.__str__ = lambda : '#PCDATA'
Text.__doc__ = """\
Text is any PCDATA content
"""

class QName(Atom):
    """
    QName(namespaceUri, qualifiedName)
    matches a fully qualified name (e.g., xsl:sort)
    """
    def __init__(self, namespaceUri, qualifiedName):
        self.qualifiedName = qualifiedName
        index = qualifiedName.rfind(':')
        if index == -1:
            local = qualifiedName
        else:
            local = qualifiedName[index+1:]
        Atom.__init__(self, (namespaceUri, local))
        return

    def __str__(self):
        return self.qualifiedName


ResultElements = Rep(Atom(CategoryTypes.RESULT_ELEMENT))
ResultElements.__str__ = lambda : '/result-elements/'
ResultElements.__doc__ = """
ResultElements is the set of elements not declared in the XSL namespace
"""

Instructions = Rep(Atom(CategoryTypes.INSTRUCTION))
Instructions.__str__ = lambda : '/instructions/'
Instructions.__doc__ = """\
Instructions is the set of elements which have a category of instruction
"""

Template = Rep(Alt(Text,
                   QName(XSL_NAMESPACE, 'xsl:variable'),
                   Atom(CategoryTypes.INSTRUCTION),
                   Atom(CategoryTypes.RESULT_ELEMENT)))
Template.__str__ = lambda : '/template/'
Template.__doc__ = """
Template is the set of text, instructions or result-elements
"""

TopLevelElements = Rep(Alt(QName(XSL_NAMESPACE, 'xsl:variable'),
                           QName(XSL_NAMESPACE, 'xsl:param'),
                           Atom(CategoryTypes.TOP_LEVEL_ELEMENT),
                           Atom(CategoryTypes.RESULT_ELEMENT)))
TopLevelElements.__str__ = lambda : '/top-level-elements/'
TopLevelElements.__doc__ = """\
TopLevelElements is the set of elements which have a category of
top-level-element or are a result-element.
"""

class Validator:
    def __init__(self, expr):
        if expr is None:
            expr = Empty
        self._expr = expr
        self._initial = {}
        expr.buildValidator(self, self._initial, {})
        return

    def __str__(self):
        return str(self._expr)

    def transition(self, token, state1, state2):
        state = state1.get(token)
        if not state:
            # this is the first one
            state1[token] = state2
        else:
            # make new epsilon state
            new_state = {}
            state1[token] = new_state
            new_state[token] = state
            new_state[ELSE] = state2
        return

    def getValidation(self):
        return self._initial
    
    def validate(self, validation, token):
        new_state = validation.get(token, -1)
        if new_state == -1 and validation.has_key(ELSE):
            new_state = validation[ELSE].get(token)
        return new_state
        
