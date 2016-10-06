########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Lib/ObjectPrint.py,v 1.2 2003/01/18 18:03:42 mbrown Exp $
"""
Pretty-printing of objects

Copyright 2003 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

import pprint as _pprint
import types as _types

def _inst_to_dict(inst):
    dict = vars(inst).copy()
    for (key, value) in dict.items():
        if type(value) is _types.InstanceType:
            dict[key] = _inst_to_dict(value)
    return dict

def pprint(object):
    if type(object) is _types.InstanceType:
        object = _inst_to_dict(object)
    _pprint.pprint(object)
        
