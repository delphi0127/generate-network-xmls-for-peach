#!/usr/bin/env python
__revision__ = '$Id: test.py,v 1.9 2005/12/08 03:19:56 uogbuji Exp $'

#import warnings
#warnings.filterwarnings('ignore')

packages = []

try:
    from Ft import Xml
    packages.extend(['Lib', 'Xml'])
except:
    pass

try:
    from Ft import Rdf
    packages.extend(['Rdf'])
except:
    pass

try:
    from Ft import Server
    packages.extend(['Server'])
except:
    pass

from Ft.Lib.TestSuite import Test
Test(name='4Suite', packages=packages)

