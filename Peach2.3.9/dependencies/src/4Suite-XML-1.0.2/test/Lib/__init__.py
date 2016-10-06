__revision__ = '$Id: __init__.py,v 1.4 2002/08/07 18:07:12 molson Exp $'



CoverageModule = 'Ft.Lib'

from Ft.Lib import ObjectPrint
from Ft import Lib
CoverageIgnored = [ObjectPrint.pprint,ObjectPrint._inst_to_dict]
