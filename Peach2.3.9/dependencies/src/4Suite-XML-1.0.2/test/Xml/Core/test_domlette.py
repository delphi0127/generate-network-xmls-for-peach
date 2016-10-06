from Ft.Xml import cDomlette

from test_domlette_interfaces import test_interface, test_access, test_mutate, test_reader_access
from test_domlette_readers import test_reader, test_oasis_suite
from test_domlette_memory import test_memory
from test_domlette_writers import test_writer
#from test_catalog import test_catalog

DOC = """<?xml version = "1.0"?>
<?xml-stylesheet href="addr_book1.xsl" type="text/xml"?>
<docelem xmlns:ft='http://fourthought.com'>
  <child foo='bar'>Some Text</child>
  <!--A comment-->
  <ft:nschild ft:foo='nsbar'>Some More Text</ft:nschild>
  <appendChild/>
</docelem>
"""

def Test(tester):

    tester.startGroup("Domlette")
    test_interface(tester, cDomlette)
    test_access(tester, cDomlette)
    test_mutate(tester, cDomlette)
    test_reader(tester, cDomlette)
    test_reader_access(tester, cDomlette, DOC)
    #test_catalog(tester, cDomlette)
    test_writer(tester, cDomlette)

    test_memory(tester, cDomlette)

    test_oasis_suite(tester, cDomlette)

    tester.groupDone()
    return

if __name__ == '__main__':
    from Ft.Lib.TestSuite import Tester
    tester = Tester.Tester()
    Test(tester)
