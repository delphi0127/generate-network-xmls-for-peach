



import os, sys

g_tests = ['create_document',
           'fetch_document',
           'update_document',
           'delete_document',
           'create_container',
           'fetch_container',
           'delete_container',
           ]


for test in g_tests:

    if len(sys.argv) > 1 and test not in sys.argv[1:]:
        continue

    print test
    cmd = 'python %s.py > %s.out' % (test,test)
    os.system(cmd)
