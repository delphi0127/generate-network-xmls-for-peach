from Ft.Lib import boolean
from Ft.Xml import EMPTY_NAMESPACE

def RangeTo(context, expr):
    """
    <location-set> range-to(<expr>)

    For each location in the context, range-to returns a range.
    """
    return []


def StringRange(context, string, startPos=1, length=None):
    """
    <location-set> string-range(<location-set>, <string>, <number>?, <number>?)

    For each location in the location-set argument, string-range returns a set
    of string ranges, a set of substrings in a string.
    """
    return []


def Range(context, locationSet):
    """
    <location-set> range(<location-set>)

    The range function returns ranges covering the locations in the argument
    location-set.  For each location x in the argument location-set, a range
    location representing the covering range of x is added to the result
    location-set.
    """
    return []


def RangeInside(context, locationSet):
    """
    <location-set> range-inside(<location-set>)

    The range-inside function returns ranges covering the content of the
    locations in the argument location-set.  For each location x in the
    argument location-set, a range location is added to the result location-set.
    """
    return []


def StartPoint(context, point):
    """
    <point> start-point(<point>)

    For each location x in the argument location-set, start-point adds a
    location of type point to the result location-set.
    """
    return []


def EndPoint(context, point):
    """
    <point> end-point(<point>)

    For each location x in the argument location-set, end-point adds a location
    of type point to the result location-set.
    """
    return []


def Here(context):
    """
    <location-set> here()

    The here function returns a location-set with a single member.  That
    location locates the node that directly contains the XPointer being
    evaluated.
    """
    return [context.originalContext]


def Origin(context):
    """
    <location-set> origin()

    The origin functions enables addressing relative to out-of-line links
    such as defined in XLink. This allows XPointers to be used in applications
    to express relative locations when links do not reside directly at one of
    their endpoints. The function returns a location-set with a single member,
    which locates the element from which a user or program initiated traversal
    of the link.
    """
    return []


def Unique(context):
    """
    <boolean> unique()

    The predicate function unique returns true if and only if context size is
    equal to 1.
    """
    return context.size == 1 and boolean.true or boolean.false


CoreFunctions = {
    (EMPTY_NAMESPACE, 'range-to') : RangeTo,
    (EMPTY_NAMESPACE, 'string-range') : StringRange,
    (EMPTY_NAMESPACE, 'range') : Range,
    (EMPTY_NAMESPACE, 'range-inside') : RangeInside,
    (EMPTY_NAMESPACE, 'start-point') : StartPoint,
    (EMPTY_NAMESPACE, 'end-point') : EndPoint,
    (EMPTY_NAMESPACE, 'here') : Here,
    (EMPTY_NAMESPACE, 'origin') : Origin,
    (EMPTY_NAMESPACE, 'unique') : Unique,
    }
