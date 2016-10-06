__revision__ = '$Id: __init__.py,v 1.7 2006/08/13 22:01:35 jkloth Exp $'

def PreprocessFiles(dirs, files):
    """
    PreprocessFiles(dirs, files) -> (dirs, files)
    
    This function is responsible for sorting and trimming the
    file and directory lists as needed for proper testing.
    """
    from Ft.Lib.TestSuite import RemoveTests, SortTests

    ignored_files = ['test_profile',
                     'test_performance_matrix',
                     'test_compilied_stylesheet',
                     'test_compiled_stylesheet',
                     'test_exslt',
                     ]
    RemoveTests(files, ignored_files)

    ordered_files = []
    SortTests(files, ordered_files)

    ignored_dirs = ['etc']
    RemoveTests(dirs, ignored_dirs)

    ordered_dirs = []
    SortTests(dirs, ordered_dirs)

    return (dirs, files)

CoverageModule = 'Ft.Xml.Xslt'

from Ft.Xml.Xslt import _4xslt
from Ft.Xml.Xslt import StylesheetTree

CoverageIgnored = [_4xslt.Run,
                   _4xslt.XsltCommandLineApp.__init__,
                   _4xslt.XsltCommandLineApp.validate_arguments,

                   StylesheetTree.XsltNode.instantiate
                   ]
