__revision__ = "$Id: __init__.py,v 1.5 2003/09/08 01:03:57 jkloth Exp $"
import sys
def PreprocessFiles(dirs, files):
    """
    PreprocessFiles(dirs, files) -> (dirs, files)
    
    This function is responsible for sorting and trimming the
    file and directory lists as needed for proper testing.
    """
    from Ft.Lib.TestSuite import RemoveTests, SortTests

    ignored_files = ['w3c_xslt_spec']
    if sys.platform.startswith("darwin"):
        ignored_files.append("ob_20000613")
    RemoveTests(files, ignored_files)

    ordered_files = []
    SortTests(files, ordered_files)

    ignored_dirs = ['etc']
    RemoveTests(dirs, ignored_dirs)

    ordered_dirs = []
    SortTests(dirs, ordered_dirs)

    ignored = ['etc']
    for dir in ignored:
        if dir in dirs:
            dirs.remove(dir)

    return (dirs, files)
