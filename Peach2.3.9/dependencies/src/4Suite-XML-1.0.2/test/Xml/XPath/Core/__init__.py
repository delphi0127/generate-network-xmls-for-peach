__revision__ = '$Id: __init__.py,v 1.7 2006/08/13 22:01:34 jkloth Exp $'

def PreprocessFiles(dirs, files):
    """
    PreprocessFiles(dirs, files) -> (dirs, files)
    
    This function is responsible for sorting and trimming the
    file and directory lists as needed for proper testing.
    """
    from Ft.Lib.TestSuite import RemoveTests, SortTests

    ignored_files = ['DummyExpr']
    RemoveTests(files, ignored_files)

    ordered_files = []
    SortTests(files, ordered_files)

    ignored_dirs = []
    RemoveTests(dirs, ignored_dirs)

    ordered_dirs = []
    SortTests(dirs, ordered_dirs)

    return (dirs, files)



CoverageModule = 'Ft.Xml.XPath'
from Ft.Xml.XPath import _4xpath
from Ft.Xml.XPath import ParsedNodeTest
CoverageIgnored = [
                   _4xpath.Run,
                   _4xpath.XPathCommandLineApp.__init__,
                   _4xpath.XPathCommandLineApp.validate_arguments,

                   # XSLT specific interfaces
                   ParsedNodeTest.LocalNameTest.getQuickKey,
                   ParsedNodeTest.NamespaceTest.getQuickKey,
                   ParsedNodeTest.ProcessingInstructionNodeTest.getQuickKey,
                   ParsedNodeTest.QualifiedNameTest.getQuickKey,
                   ]
