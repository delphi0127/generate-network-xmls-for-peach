
Peach 2 Unittests
-----------------

These are unittests for Peach 2.  See template.py/template.xml and utils.py.
Currently the tests are no were near complete, but we are making progress.

The framework for creating tests still needs to be flushed out, some of
the stuff has been staked out in utils.py, but needs implementation.

If the test case only needs a count or parse test (peach.py [-c|-t]) then
you can just create a file name parsingCountN.xml or parsingTestN.xml were
N is the next available number.  parsing.py will then perform the needed
actions against the files.

3/4/08
-mike
