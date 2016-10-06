__revision__ = '$Id: __init__.py,v 1.1 2005/02/14 00:15:51 jkloth Exp $'

def PreprocessFiles(dirs, files):
    """
    PreprocessFiles(dirs, files) -> (dirs, files)
    
    This function is responsible for sorting and trimming the
    file and directory lists as needed for proper testing.
    """
    from Ft.Lib.TestSuite import RemoveTests, SortTests

    ignored_files = []
    RemoveTests(files, ignored_files)

    ordered_files = []
    SortTests(files, ordered_files)

    ignored_dirs = []
    RemoveTests(dirs, ignored_dirs)

    ordered_dirs = []
    SortTests(dirs, ordered_dirs)

    return (dirs, files)

# -- Coverage testing settings -----------------------------------------

CoverageModule = 'Ft.Xml.Xslt.Exslt'
CoverageIgnored = []
