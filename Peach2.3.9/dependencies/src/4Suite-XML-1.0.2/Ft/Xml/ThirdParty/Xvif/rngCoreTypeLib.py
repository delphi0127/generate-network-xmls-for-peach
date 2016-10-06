import re

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

class stringType(unicode):
 """
    This class is strictly identical to the python's unicode type
 """

class tokenType(unicode):

    def __new__(cls, value=""):
        return unicode.__new__(cls, re.sub("[\n\t ]+", " ", value).strip())

