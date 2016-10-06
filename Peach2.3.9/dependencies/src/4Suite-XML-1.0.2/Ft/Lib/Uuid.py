########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Lib/Uuid.py,v 1.8 2004/08/05 21:57:32 mbrown Exp $
"""
Functions for generating and comparing Universal Unique Identifiers
(UUIDs), based on ideas from e2fsprogs.

A UUID is essentially a 128-bit random number that has a string
representation of 28 hexadecimal digits, hyphenated in groups of
8-4-4-12. The value could be greater than the number of atoms in the
universe; it's extremely unlikely that the same number would ever be
generated twice.

UUIDs are defined by ISO/IEC 11578:1996 (Remote Procedure Call)
and The Open Group's DCE 1.1 (Distributed Computing Environment) spec
(the ISO version was based on an earlier version of the DCE spec).
See http://www.opengroup.org/onlinepubs/009629399/apdxa.htm#tagcjh_20
for the current version, and also see the expired IETF Internet-Draft
http://www.opengroup.org/dce/info/draft-leach-uuids-guids-01.txt for
a version with more informative prose and examples.

Copyright 2004 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

import socket

from Random import GetRandomBytes


def GenerateUuid():
    """Returns a new UUID as a long int"""
    result = GetRandomBytes(16)
    result = result[:6] + chr((ord(result[6]) & 0x4F) | 0x40) + result[7:8] + chr((ord(result[8]) & 0xBF) | 0x80) + result[9:]

    res = 0L
    for i in range(16):
        res = (res << 8) + ord(result[i] )

    return res


def UuidAsString(uuid):
    """
    Formats a long int representing a UUID as a UUID string:
    32 hex digits in hyphenated groups of 8-4-4-4-12.
    """
    ## Python 2.0+
    s = '%032x' % uuid
    ## Python 1.5+
    #s = string.replace(string.lower('%032s' % hex(uuid)[2:-1]),' ','0')
    return '%s-%s-%s-%s-%s' % (s[0:8],s[8:12],s[12:16],s[16:20],s[20:])

    ## Uche wants to keep this around.
    ## Note that it does not 0-pad the number; this needs to be fixed.
    #newUuid = ''
    #curUuid = uuid
    #for ctr in range(16):
    #    num = int(curUuid & 0xFF)
    #    newChar = chr(num)
    #    curUuid = curUuid >> 8
    #    newUuid = newChar + newUuid
    #
    #uuid = newUuid
    #
    #result = ''
    ##This could of course be a function, but the overhead is undesirable
    #mult = 0x1000000L
    #num = 0
    #ix = 0
    #while mult:
    #    num = num + mult * ord(uuid[ix])
    #    mult = mult / 0x100
    #    ix = ix + 1
    #result = result + hex(num)[2:-1] + '-'
    #mult = 0x100
    #num = 0
    #while mult:
    #    num = num + mult * ord(uuid[ix])
    #    mult = mult / 0x100
    #    ix = ix + 1
    #result = result + hex(num)[2:] + '-'
    #mult = 0x100
    #num = 0
    #while mult:
    #    num = num + mult * ord(uuid[ix])
    #    mult = mult / 0x100
    #    ix = ix + 1
    #result = result + hex(num)[2:] + '-'
    #mult = 0x100
    #num = 0
    #while mult:
    #    num = num + mult * ord(uuid[ix])
    #    mult = mult / 0x100
    #    ix = ix + 1
    #result = result + hex(num)[2:] + '-'
    #mult = 0x1000000L
    #num = 0
    #while mult:
    #    num = num + mult * ord(uuid[ix])
    #    mult = mult / 0x100
    #    ix = ix + 1
    #result = result + hex(num)[2:-1]
    #mult = 0x100
    #num = 0
    #while mult:
    #    num = num + mult * ord(uuid[ix])
    #    mult = mult / 0x100
    #    ix = ix + 1
    #result = result + hex(num)[2:]
    #return result.lower()


def CompareUuids(u1, u2):
    """Compares, as with cmp(), two UUID strings case-insensitively"""
    return cmp(u1.upper(), u2.upper())

