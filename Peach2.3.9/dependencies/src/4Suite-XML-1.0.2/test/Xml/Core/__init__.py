__revision__ = '$Id: __init__.py,v 1.12 2005/11/15 02:22:41 jkloth Exp $'

def PreprocessFiles(dirs, files):
    """
    PreprocessFiles(dirs, files) -> (dirs, files)

    This function is responsible for sorting and trimming the
    file and directory lists as needed for proper testing.
    """
    from Ft.Lib.TestSuite import RemoveTests, SortTests

    ignored_files = ['test_domlette_readers',
                     'test_domlette_interfaces',
                     'test_domlette_memory',
                     'test_domlette_writers',
                     'test_catalog',
                     'test_ranges', # only supported by 4DOM
                     'test_get_all_ns',
                     'test_string_strip',
                     'test_split_qname',
                     ]
    RemoveTests(files, ignored_files)

    ordered_files = ['test_domlette', 'test_saxlette']
    SortTests(files, ordered_files)

    ignored_dirs = []
    RemoveTests(dirs, ignored_dirs)

    ordered_dirs = []
    SortTests(dirs, ordered_dirs)

    return (dirs, files)
