__revision__ = '$Id: __init__.py,v 1.11 2005/02/14 00:15:50 jkloth Exp $'

from Ft.Lib.TestSuite import TestMode

def PreprocessFiles(dirs, files):
    """
    PreprocessFiles(dirs, files) -> (dirs, files)

    This function is responsible for sorting and trimming the
    file and directory lists as needed for proper testing.
    """
    from Ft.Lib.TestSuite import RemoveTests, SortTests

    ignored_files = ['test_harness']
    RemoveTests(files, ignored_files)

    ordered_files = []
    SortTests(files, ordered_files)

    ignored_dirs = []
    RemoveTests(dirs, ignored_dirs)

    ordered_dirs = ['Core', 'Exslt', 'Borrowed']
    SortTests(dirs, ordered_dirs)

    return (dirs, files)

# -- run modes -------------------------------------------------------

class _XsltMode(TestMode.TestMode):

    def _init(self, tester):
        return 1

    def _pre(self, tester):
        tester.test_data['source'] = self.name
        tester.test_data['module'] = __import__('Ft.Xml.' + self.name,
                                                {}, {}, ['*'])
        return

MODES = [_XsltMode('cDomlette', default=1),
         ]
