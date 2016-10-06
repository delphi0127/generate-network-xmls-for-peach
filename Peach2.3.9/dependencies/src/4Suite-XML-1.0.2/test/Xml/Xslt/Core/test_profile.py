from Ft.Xml import pDomlette
Reader = pDomlette.PyExpatReader()
import os
import profile
from Ft.Xml.Xslt import Processor
import tempfile
import pstats

tests = [#('profile_data/match.xml','profile_data/match.xsl'),
         ('profile_data/xcem100.xml','profile_data/test1.xsl'),
         ]


def profile_test(proc,xmlFile,xsltFiles):

    for xslt in xsltFiles:
        proc.appendStylesheetFile(xslt)
    print proc.runNode(xmlFile)

    


def run_test(outFile,xmlFile,stylesheets):


    tempFileName = tempfile.mktemp()
    p = Processor.Processor()
    prof = profile.Profile()

    prof.runctx("profile_test(p,xmlFile,stylesheets)",globals(),locals())
    prof.dump_stats(tempFileName)

    return tempFileName


def test(fileName):

            
    f = open(fileName,'w')
    oldOut = sys.stdout
    sys.stdout = f
    print "Profile Run"

    for t in tests:
        inFile = Reader.fromStream(open(t[0]))
        print "Begin run of %s" % t[0]
        sf = run_test(fileName,inFile,[t[1]])
        print "Dump Stats for %s" % t[0]
        pstat = pstats.Stats(sf)

        print "Sorted by total cumulative time"
        pstat.strip_dirs().sort_stats('time').print_stats(100)
        print "Sorted by number calls time"
        pstat.strip_dirs().sort_stats('calls').print_stats(100)
        print "A listing of who called whom"
        pstat.print_callers(50)
        print "A listing of who was called by whom"
        pstat.print_callees(50)
        del pstat
        os.unlink(sf)

    sys.stdout = oldOut


if __name__ == '__main__':

    import sys
    outFile = "profile.out"
    if len(sys.argv) > 1:
        outFile = sys.argv[1]
    test(outFile)
