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

    - Uche Ogbuji <uche.ogbuji@fourthought.com> (with regexp)
    - Martin v. Loewis <martin@v.loewis.de> (version with count)
"""

"""

Note that you don't need this library when using a 
Python interpreter compiled with  --enable-unicode=ucs4


"""

"""
Can't be used (known bug)

SP_PAT = re.compile(u"[\uD800-\uDBFF][\uDC00-\uDFFF]")

def smart_len(u):
    sp_count = len(SP_PAT.findall(u))
    return len(u) - sp_count
"""

def smart_len(s):
    l = 0
    for c in s:
        if not 0xd800 <= ord(c) < 0xdc00:
        # skip high surrogates - only count the low surrogates
            l += 1
    return l

