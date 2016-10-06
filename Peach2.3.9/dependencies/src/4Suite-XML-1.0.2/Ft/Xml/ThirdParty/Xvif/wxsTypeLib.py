import re, time
import rng
import rngCoreTypeLib

from Ft.Lib.Regex import W3cRegexToPyRegex
from Ft.Lib.Uri import MatchesUriRefSyntax, PercentEncode

"""
The contents of this file are subject to the Mozilla Public License
Version 1.1 (the "License"); you may not use this file except in
compliance with the License.
You may obtain a copy of the License at http://www.mozilla.org/MPL/
Software distributed under the License is distributed on an "AS IS"
basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See the
License for the specific language governing rights and limitations under
the License.

The Original Code is available at http://downloads.xmlschemata.org/python/xvif/

The Initial Developer of the Original Code is Eric van der Vlist. Portions
created by Eric van der Vlist are Copyright (C) 2002. All Rights Reserved.

Relax NG is a specification edited by the OASIS RELAX NG Technical Committee:
http://www.oasis-open.org/committees/relax-ng/

This implementation uses the implementation notes written by James Clark:
http://www.thaiopensource.com/relaxng/implement.html

Contributor(s):

"""

"""

A type library is a module with a set of classes with a "Type" suffix.

The association with the datatype URI is done through the "typeLibraries"
variable of the rng.RngParser class.

The library modules are loaded dynamically and the association between a
type and the class implementing it is done by introspection.


"""

"""
A type can have a state it manages across all instances (for a given parse
or process).  As an example, the IDType and IDREFType can optionally use
state governing the IDs used in order to manage uniqueness and reference
constraints.

By default RELAX NG does not require such referential checking, but type
classes allow a processor to optionally perform such checks.

Any type class that is stateful has a flag on it stateful=true.
The processor can check for this flag.  Classes with the stateful flag
accept a second initializer argument, state, which is a Python
dictionary that is managed for uniqueness and concurrency
by the processor.  The class can then insert and check for values as
needed.

A data type class with stateful can also have a finalize() static method,
which should be called
by the processor after the parse or process in order to check postconditions
As an example, the IDREF type has a postcondition that all values of
IDREF used should correspond to an ID value used in the same parse/process

A data type class that has no postcondition semantics should not define a finalize()
static method.  A processor should check that a data type class defines finalize()
before calling it
"""

BASE_URI = "http://www.w3.org/2001/XMLSchema-datatypes"


class _Lexical(object):

    def __init__(self):
        self.lexical = self

    if len(u'\U00010800') == 1:
        def lengthFacet(self, value):
            return len(self.lexical) == int(value)
    else:
        def lengthFacet(self, value):
            import Smart_len
            return Smart_len.smart_len(self) == int(value)


class stringType(rngCoreTypeLib.stringType, _Lexical):
    """ """
    def __init__(self, value):
        rngCoreTypeLib.stringType.__init__(self, value)
        _Lexical.__init__(self)

    def maxLengthFacet(self, value):
        return len(self) <= int(value)

    def minLengthFacet(self, value):
        return len(self) >= int(value)

    def patternFacet(self, value):
        m = re.match(W3cRegexToPyRegex(value), self)
        return m and m.end() == len(self) or False


class normalizedStringType(str):
    def __new__(cls, value=""):
        return unicode.__new__(cls, re.sub("[\n\t]", " ", value))

class tokenType(rngCoreTypeLib.tokenType, _Lexical):
    """
    Strictly identical to the token builtin class
    """
    def __init__(self, value):
        rngCoreTypeLib.tokenType.__init__(self, value)
        _Lexical.__init__(self)

class IDType(rngCoreTypeLib.tokenType, _Lexical):
    """
    Similar to the token builtin class
    """
    #FIXME: Doesn't yet handle the "Validity constraint: One ID per Element Type    #--No element type may have more than one ID attribute specified.
    #(from http://www.w3.org/TR/2000/WD-xml-2e-20000814#NT-TokenizedType)

    stateful = True

    def __init__(self, value, state=None):
        #This super class takes care of the value constraints
        rngCoreTypeLib.tokenType.__init__(self, value)
        _Lexical.__init__(self)
        if state is not None:
            ids = state.setdefault((BASE_URI, 'ID', {}))
            if value in ids:
                raise ValueError("Validity Error: duplicate ID '%s'"%value)
            ids[value] = None
        return


class IDREFType(rngCoreTypeLib.tokenType, _Lexical):
    """
    Similar to the token builtin class
    """
    stateful = True

    def __init__(self, value, state=None):
        #This super class takes care of the value constraints
        rngCoreTypeLib.tokenType.__init__(self, value)
        _Lexical.__init__(self)
        if state is not None:
            idrefs = state.setdefault((BASE_URI, 'IDREF', {}))
            idrefs[value] = None
        return

    def finalize(state):
        ids = state.setdefault((BASE_URI, 'ID', {}))
        idrefs = state.setdefault((BASE_URI, 'IDREF', {}))
        for idref in idrefs.keys():
            if idref in ids:
                raise ValueError("Validity Error: IDREF '%s' doesn't match any ID"%value)
        return
    finalize = staticmethod(finalize)


class _Bounded:

    def __init__(self, value):
        if self.__class__.max != None and self > self.__class__.max:
            raise ValueError
        if self.__class__.min != None and self < self.__class__.min:
            raise ValueError


class _Ordered:

    def maxExclusiveFacet(self, value):
        return self < self.__class__(value)

    def maxInclusiveFacet(self, value):
        return self <= self.__class__(value)

    def minExclusiveFacet(self, value):
        return self > self.__class__(value)

    def minInclusiveFacet(self, value):
        return self >= self.__class__(value)

class _Numeric(_Ordered):

    def totalDigitsFacet(self, value):
        if self < 0:
            return len(str(self)) -1 <= value
        else:
            return len(str(self))  <= value


class integerType(long, _Numeric):
    """
    """

class nonPositiveIntegerType(_Bounded, integerType):

    min=None
    max=0

class nonNegativeIntegerType(_Bounded, integerType):

    min=0
    max=None

class positiveIntegerType(_Bounded, integerType):

    min=1
    max=None

class negativeIntegerType(_Bounded, integerType):

    min=None
    max=-1

class unsignedLongType(_Bounded, integerType):

    min=0
    max=18446744073709551615L

class unsignedIntType(_Bounded, integerType):

    min=0
    max=4294967295L

class longType(_Bounded, integerType):

    min = -9223372036854775808L
    max =  9223372036854775807L


class intType(int, _Numeric):
    """
    """

class shortType(_Bounded, intType):

    min = -32768
    max =  32767

class unsignedShortType(_Bounded, intType):

    min = 0
    max = 65535

class byteType(_Bounded, intType):

    min = -128
    max =  127

class unsignedByteType(_Bounded, intType):

    min = 0
    max = 255

class decimalType(_Numeric):

    def __init__(self, value):
        value = tokenType(unicode(value))
        if re.match("^[+-]?([0-9]*\.[0-9]+|[0-9]+\.?[0-9]*)$", value):
            try:
                i, d = value.split('.')
            except ValueError:
                i = value
                d=""
            # d = d.rstrip("0")
            d = re.sub("0*$", "", d)
            self.val = long("%s%s" % (i,d))
            self.power = len(d)
            self.value = value
        else:
            raise ValueError

    def __cmp__(self, other):
        if other.__class__ != decimalType:
            other = decimalType(other)
        if self.power < other.power:
            o = other.val
            s = self.val * 10 **  (other.power - self.power)
        else:
            s = self.val
            o = other.val * 10 **  (self.power - other.power)
        return s.__cmp__(o)

    def fractionDigitsFacet(self, value):
        return self.power <= value

    def totalDigitsFacet(self, value):
        if self.val < 0:
            return len(str(self.val)) -1 <= value
        else:
            return len(str(self.val))  <= value

floatType = decimalType

class dateType(_Ordered):

    formatWoTZ = "%Y-%m-%d"
    formatZ = "%Y-%m-%dZ"

    def __init__(self, value):
        self.lexical = tokenType(value)
        if not re.match("[ \t\n]*[0-9]+-[0-9]{2}-[0-9]{2}Z?", value):
            raise ValueError
        try:
            self.value = time.strptime(value, dateType.formatWoTZ)
            self.tz = 0
        except ValueError:
            self.value = time.strptime(value, dateType.formatZ)
            self.tz = 1
        if self.value[2] == 31 and not self.value[1] in (1, 3, 5, 7, 8, 10, 12):
            raise ValueError
        if self.value[2] == 30 and self.value[1] == 2:
            raise ValueError
        if self.value[2] == 29 and self.value[1] == 2 and ((self.value[0] % 4 != 0) or (self.value[0] % 100 == 0)):
            raise ValueError

    def __cmp__(self, other):
        if other.__class__ != dateType:
            other = dateType(other)
        for i in range (0, 5):
            res = self.value[i].__cmp__(other.value[i])
            if res != 0:
                return res
        return 0


class booleanType(rngCoreTypeLib.stringType, _Lexical):
    """ """
    def __init__(self, value):
        rngCoreTypeLib.stringType.__init__(self, value)
        _Lexical.__init__(self)
        if value not in ['1','0','true','false']:
            raise ValueError


class timeType(_Ordered):
    def __init__(self,value):
        try:
            #Make use of datetime module (if available)
            import datetime
            from TimeLib import parse_isotime
            self.value=parse_isotime(value)
            if not self.value:
                raise ValueError

        except:
            #Use Ft.Lib.Time as a fallback
            from Ft.Lib.Time import FromISO8601
            try:
                self.value=FromISO8601(value)
            except:
                raise ValueError

class dateTimeType(_Ordered):
    def __init__(self,value):
        try:
            #Make use of datetime module (if available)
            import datetime
            from TimeLib import parse_isodate
            self.value=parse_isodate(value)
            if not self.value:
                raise ValueError

        except:
            #Use Ft.Lib.Time as a fallback
            from Ft.Lib.Time import FromISO8601
            try:
                self.value=FromISO8601(value)
            except:
                raise ValueError

class anyURIType(_Lexical):
    """
    anyURI is somewhat of a misnomer;
    it is really a URI reference *or* IRI reference.
    """
    def __init__(self, value):
        # After URI-disallowed characters are percent-encoded,
        # the result must be an RFC 2396+2732 URI reference.
        # RFC 3986/STD 66 did not change the disallowed set,
        # so it is safe to use Ft.Lib.Uri to test the value.
        escaped = PercentEncode(value, encodeReserved=False)
        if not MatchesUriRefSyntax(escaped):
            raise ValueError

